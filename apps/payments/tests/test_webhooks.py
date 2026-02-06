"""Tests for Stripe webhook handling."""

import json
from unittest.mock import MagicMock
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client
from django.test import TestCase
from django.test import override_settings
from stripe import SignatureVerificationError

from apps.payments.views import _dispatch_webhook
from apps.payments.views import _handle_checkout_session
from apps.payments.views import _handle_invoice_upcoming
from apps.payments.views import _handle_subscription_deleted
from apps.payments.views import _handle_subscription_dispute_created
from apps.payments.views import _handle_subscription_paused
from apps.payments.views import _handle_subscription_resumed
from apps.payments.views import _handle_subscription_updated

User = get_user_model()


class WebhookSignatureVerificationTest(TestCase):
    """Tests for Stripe webhook signature verification."""

    def setUp(self):
        self.client = Client()
        self.webhook_url = "/payments/webhook/"

    @override_settings(STRIPE_WEBHOOK_SECRET="whsec_test_secret")  # noqa: S106
    @patch("apps.payments.views.stripe.Webhook.construct_event")
    def test_valid_signature_processes_event(self, mock_construct):
        """Test that valid webhook signature allows event processing."""
        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {"object": {"id": "cs_123", "metadata": {}}},
        }

        response = self.client.post(
            self.webhook_url,
            data=json.dumps({"type": "checkout.session.completed"}),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="t=123,v1=abc",
        )

        assert response.status_code == 200  # noqa: PLR2004

    @override_settings(STRIPE_WEBHOOK_SECRET="whsec_test_secret")  # noqa: S106
    @patch("apps.payments.views.stripe.Webhook.construct_event")
    def test_invalid_signature_returns_400(self, mock_construct):
        """Test that invalid signature returns 400 error."""
        mock_construct.side_effect = SignatureVerificationError(
            message="Invalid signature", sig_header="invalid"
        )

        response = self.client.post(
            self.webhook_url,
            data=json.dumps({"type": "test"}),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="invalid_sig",
        )

        assert response.status_code == 400  # noqa: PLR2004

    def test_invalid_json_payload_returns_400(self):
        """Test that invalid JSON payload returns 400 error."""
        response = self.client.post(
            self.webhook_url,
            data="not valid json",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="t=123,v1=abc",
        )

        assert response.status_code == 400  # noqa: PLR2004

    @override_settings(STRIPE_WEBHOOK_SECRET="")
    @patch("apps.payments.views.stripe.Event.construct_from")
    def test_no_webhook_secret_uses_event_construct(self, mock_construct):
        """Test that missing webhook secret falls back to Event.construct_from."""
        mock_construct.return_value = MagicMock(
            get=MagicMock(
                side_effect=lambda k, d=None: {
                    "type": "test.event",
                    "data": {"object": {}},
                }.get(k, d)
            )
        )

        response = self.client.post(
            self.webhook_url,
            data=json.dumps({"type": "test.event"}),
            content_type="application/json",
        )

        assert response.status_code == 200  # noqa: PLR2004


class WebhookDispatchTest(TestCase):
    """Tests for webhook event dispatching to handlers."""

    def test_dispatch_checkout_session_completed(self):
        """Test that checkout.session.completed event is dispatched correctly."""
        event = {
            "type": "checkout.session.completed",
            "data": {"object": {"id": "cs_123", "metadata": {}}},
        }

        with patch("apps.payments.views._handle_checkout_session") as mock_handler:
            _dispatch_webhook(event)
            mock_handler.assert_called_once_with({"id": "cs_123", "metadata": {}})

    def test_dispatch_async_payment_succeeded(self):
        """Test that async_payment_succeeded is dispatched correctly."""
        event = {
            "type": "checkout.session.async_payment_succeeded",
            "data": {"object": {"id": "cs_456", "metadata": {}}},
        }

        with patch("apps.payments.views._handle_checkout_session") as mock_handler:
            _dispatch_webhook(event)
            mock_handler.assert_called_once()

    def test_dispatch_unknown_event_type(self):
        """Test that unknown event types are logged but don't error."""
        event = {
            "type": "unknown.event.type",
            "data": {"object": {}},
        }

        _dispatch_webhook(event)


class CheckoutSessionWebhookTest(TestCase):
    """Tests for checkout.session.completed webhook handling."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="checkout@example.com",
            password="testpass123",  # noqa: S106
        )

    @patch("apps.payments.views.stripe.Customer.modify")
    def test_checkout_session_links_customer_to_user(self, mock_modify):
        """Test that checkout completion links Stripe customer to user."""
        session = {
            "id": "cs_test123",
            "customer": "cus_checkout123",
            "metadata": {"user_id": str(self.user.pk)},
        }

        _handle_checkout_session(session)

        self.user.refresh_from_db()
        assert self.user.stripe_customer_id == "cus_checkout123"

    @patch("apps.payments.views.stripe.Customer.modify")
    def test_checkout_session_sets_membership_true(self, mock_modify):
        """Test that checkout completion sets has_membership=True for subscriptions."""
        session = {
            "id": "cs_sub123",
            "customer": "cus_sub123",
            "metadata": {"user_id": str(self.user.pk)},
        }

        _handle_checkout_session(session)

        self.user.refresh_from_db()
        assert self.user.has_membership is True
        assert self.user.membership_paused is False

    def test_checkout_session_missing_metadata(self):
        """Test that missing user metadata is handled gracefully."""
        session = {
            "id": "cs_no_meta",
            "customer": "cus_nometa",
            "metadata": {},
        }

        _handle_checkout_session(session)

    def test_checkout_session_nonexistent_user(self):
        """Test that nonexistent user ID is handled gracefully."""
        session = {
            "id": "cs_bad_user",
            "customer": "cus_baduser",
            "metadata": {"user_id": "99999"},
        }

        _handle_checkout_session(session)


class SubscriptionWebhookTest(TestCase):
    """Tests for subscription-related webhook handlers."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="subscriber@example.com",
            password="testpass123",  # noqa: S106
            stripe_customer_id="cus_subscriber",
            has_membership=True,
            membership_paused=False,
        )

    def test_subscription_deleted_removes_membership(self):
        """Test that subscription deletion removes membership."""
        subscription = {
            "id": "sub_deleted",
            "customer": "cus_subscriber",
        }

        _handle_subscription_deleted(subscription)

        self.user.refresh_from_db()
        assert self.user.has_membership is False
        assert self.user.membership_paused is False

    def test_subscription_deleted_missing_customer(self):
        """Test that subscription deletion without customer ID is handled."""
        subscription = {"id": "sub_no_customer"}

        _handle_subscription_deleted(subscription)

    def test_subscription_updated_active_status(self):
        """Test that active subscription status keeps membership active."""
        self.user.has_membership = False
        self.user.save()

        subscription = {
            "id": "sub_active",
            "customer": "cus_subscriber",
            "status": "active",
        }

        _handle_subscription_updated(subscription)

        self.user.refresh_from_db()
        assert self.user.has_membership is True
        assert self.user.membership_paused is False

    def test_subscription_updated_trialing_status(self):
        """Test that trialing status keeps membership active."""
        subscription = {
            "id": "sub_trial",
            "customer": "cus_subscriber",
            "status": "trialing",
        }

        _handle_subscription_updated(subscription)

        self.user.refresh_from_db()
        assert self.user.has_membership is True
        assert self.user.membership_paused is False

    def test_subscription_updated_past_due_pauses_membership(self):
        """Test that past_due status pauses membership."""
        subscription = {
            "id": "sub_pastdue",
            "customer": "cus_subscriber",
            "status": "past_due",
        }

        _handle_subscription_updated(subscription)

        self.user.refresh_from_db()
        assert self.user.has_membership is True
        assert self.user.membership_paused is True

    def test_subscription_updated_unpaid_pauses_membership(self):
        """Test that unpaid status pauses membership."""
        subscription = {
            "id": "sub_unpaid",
            "customer": "cus_subscriber",
            "status": "unpaid",
        }

        _handle_subscription_updated(subscription)

        self.user.refresh_from_db()
        assert self.user.has_membership is True
        assert self.user.membership_paused is True

    def test_subscription_updated_canceled_removes_membership(self):
        """Test that canceled status removes membership."""
        subscription = {
            "id": "sub_canceled",
            "customer": "cus_subscriber",
            "status": "canceled",
        }

        _handle_subscription_updated(subscription)

        self.user.refresh_from_db()
        assert self.user.has_membership is False
        assert self.user.membership_paused is False

    def test_subscription_updated_incomplete_expired_removes_membership(self):
        """Test that incomplete_expired status removes membership."""
        subscription = {
            "id": "sub_incomplete",
            "customer": "cus_subscriber",
            "status": "incomplete_expired",
        }

        _handle_subscription_updated(subscription)

        self.user.refresh_from_db()
        assert self.user.has_membership is False

    def test_subscription_updated_paused_status(self):
        """Test that paused status pauses membership."""
        subscription = {
            "id": "sub_paused",
            "customer": "cus_subscriber",
            "status": "paused",
        }

        _handle_subscription_updated(subscription)

        self.user.refresh_from_db()
        assert self.user.has_membership is True
        assert self.user.membership_paused is True

    def test_subscription_paused_event(self):
        """Test that subscription.paused event pauses membership."""
        subscription = {
            "id": "sub_pause_event",
            "customer": "cus_subscriber",
        }

        _handle_subscription_paused(subscription)

        self.user.refresh_from_db()
        assert self.user.membership_paused is True

    def test_subscription_resumed_event(self):
        """Test that subscription.resumed event unpauses membership."""
        self.user.membership_paused = True
        self.user.save()

        subscription = {
            "id": "sub_resume_event",
            "customer": "cus_subscriber",
        }

        _handle_subscription_resumed(subscription)

        self.user.refresh_from_db()
        assert self.user.membership_paused is False

    def test_subscription_dispute_pauses_membership(self):
        """Test that dispute pauses membership for subscription users."""
        dispute = {
            "id": "dp_sub123",
            "customer": "cus_subscriber",
            "charge": "ch_dispute",
            "amount": 2999,
        }

        _handle_subscription_dispute_created(dispute)

        self.user.refresh_from_db()
        assert self.user.membership_paused is True

    @patch("apps.payments.views._resolve_customer_from_charge")
    def test_subscription_dispute_resolves_customer_from_charge(self, mock_resolve):
        """Test that dispute resolves customer from charge when missing from object."""
        mock_resolve.return_value = "cus_subscriber"

        dispute = {
            "id": "dp_no_customer",
            "charge": "ch_dispute2",
            "amount": 1999,
        }

        _handle_subscription_dispute_created(dispute)

        self.user.refresh_from_db()
        assert self.user.membership_paused is True

    def test_invoice_upcoming_logs_info(self):
        """Test that upcoming invoice event is handled without error."""
        invoice = {
            "id": "in_upcoming",
            "customer": "cus_subscriber",
        }

        _handle_invoice_upcoming(invoice)
