"""Tests for Stripe checkout session creation and customer portal."""

from unittest.mock import MagicMock
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client
from django.test import TestCase
from django.test import override_settings
from stripe import InvalidRequestError
from stripe import StripeError

User = get_user_model()


class CheckoutSessionViewTest(TestCase):
    """Tests for the create_checkout_session view."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="checkout_user@example.com",
            password="testpass123",  # noqa: S106
        )
        self.client = Client()
        self.client.force_login(self.user)
        self.checkout_url = "/payments/checkout/price_test123/"

    def test_checkout_requires_login(self):
        """Test that checkout endpoint requires authentication."""
        self.client.logout()
        response = self.client.get(self.checkout_url)
        assert response.status_code == 302  # noqa: PLR2004
        assert "/accounts/login/" in response.url or "/login/" in response.url

    @patch("apps.payments.views.stripe.checkout.Session.create")
    @patch("apps.payments.views.stripe.Price.retrieve")
    @patch("apps.payments.views.stripe.Customer.create")
    @override_settings(STRIPE_SECRET_KEY="sk_test_123")  # noqa: S106
    def test_checkout_creates_session_for_new_customer(
        self, mock_customer_create, mock_price_retrieve, mock_session_create
    ):
        """Test that checkout creates Stripe customer and session for new users."""
        mock_customer_create.return_value = {"id": "cus_new_checkout"}
        mock_price_retrieve.return_value = {"id": "price_test123"}
        mock_session_create.return_value = MagicMock(
            url="https://checkout.stripe.com/session123"
        )

        response = self.client.get(self.checkout_url)

        assert response.status_code == 303  # noqa: PLR2004
        mock_customer_create.assert_called_once()
        mock_session_create.assert_called_once()

        session_kwargs = mock_session_create.call_args[1]
        assert session_kwargs["customer"] == "cus_new_checkout"
        assert session_kwargs["line_items"][0]["price"] == "price_test123"
        assert session_kwargs["line_items"][0]["quantity"] == 1

    @patch("apps.payments.views.stripe.checkout.Session.create")
    @patch("apps.payments.views.stripe.Price.retrieve")
    @patch("apps.payments.views.stripe.Customer.retrieve")
    @override_settings(STRIPE_SECRET_KEY="sk_test_123")  # noqa: S106
    def test_checkout_uses_existing_customer(
        self, mock_customer_retrieve, mock_price_retrieve, mock_session_create
    ):
        """Test that checkout uses existing Stripe customer ID."""
        self.user.stripe_customer_id = "cus_existing_checkout"
        self.user.save()

        mock_customer_retrieve.return_value = {"id": "cus_existing_checkout"}
        mock_price_retrieve.return_value = {"id": "price_test123"}
        mock_session_create.return_value = MagicMock(
            url="https://checkout.stripe.com/session456"
        )

        response = self.client.get(self.checkout_url)

        assert response.status_code == 303  # noqa: PLR2004
        mock_customer_retrieve.assert_called_once_with("cus_existing_checkout")

        session_kwargs = mock_session_create.call_args[1]
        assert session_kwargs["customer"] == "cus_existing_checkout"

    @patch("apps.payments.views.stripe.Price.retrieve")
    @patch("apps.payments.views.stripe.Customer.create")
    @override_settings(STRIPE_SECRET_KEY="sk_test_123")  # noqa: S106
    def test_checkout_invalid_price_returns_400(
        self, mock_customer_create, mock_price_retrieve
    ):
        """Test that invalid price ID returns 400 error."""
        mock_customer_create.return_value = {"id": "cus_test"}
        mock_price_retrieve.side_effect = InvalidRequestError(
            message="No such price", param="price"
        )

        response = self.client.get(self.checkout_url)

        assert response.status_code == 400  # noqa: PLR2004
        assert b"Invalid price ID" in response.content

    @patch("apps.payments.views.stripe.Customer.create")
    @override_settings(STRIPE_SECRET_KEY="sk_test_123")  # noqa: S106
    def test_checkout_stripe_error_returns_400(self, mock_customer_create):
        """Test that Stripe API error returns 400."""
        mock_customer_create.side_effect = StripeError("API Error")

        response = self.client.get(self.checkout_url)

        assert response.status_code == 400  # noqa: PLR2004

    @override_settings(STRIPE_SECRET_KEY="")
    def test_checkout_no_stripe_key_returns_500(self):
        """Test that missing Stripe key returns 500 error."""
        with patch("apps.payments.views.stripe_api_key", ""):
            response = self.client.get(self.checkout_url)
            assert response.status_code in [400, 500]

    @patch("apps.payments.views.stripe.checkout.Session.create")
    @patch("apps.payments.views.stripe.Price.retrieve")
    @patch("apps.payments.views.stripe.Customer.create")
    @override_settings(STRIPE_SECRET_KEY="sk_test_123")  # noqa: S106
    def test_checkout_subscription_mode_includes_trial(
        self, mock_customer_create, mock_price_retrieve, mock_session_create
    ):
        """Test that subscription checkout includes trial period."""
        mock_customer_create.return_value = {"id": "cus_sub_test"}
        mock_price_retrieve.return_value = {"id": "price_test123"}
        mock_session_create.return_value = MagicMock(
            url="https://checkout.stripe.com/sub"
        )

        self.client.get(self.checkout_url)

        session_kwargs = mock_session_create.call_args[1]
        assert session_kwargs["mode"] == "subscription"
        assert "subscription_data" in session_kwargs
        assert session_kwargs["subscription_data"]["trial_period_days"] == 7  # noqa: PLR2004

    @patch("apps.payments.views.stripe.checkout.Session.create")
    @patch("apps.payments.views.stripe.Price.retrieve")
    @patch("apps.payments.views.stripe.Customer.create")
    @override_settings(STRIPE_SECRET_KEY="sk_test_123")  # noqa: S106
    def test_checkout_subscription_includes_metadata(
        self, mock_customer_create, mock_price_retrieve, mock_session_create
    ):
        """Test that subscription checkout includes user metadata."""
        mock_customer_create.return_value = {"id": "cus_meta_test"}
        mock_price_retrieve.return_value = {"id": "price_test123"}
        mock_session_create.return_value = MagicMock(
            url="https://checkout.stripe.com/meta"
        )

        self.client.get(self.checkout_url)

        session_kwargs = mock_session_create.call_args[1]
        assert "metadata" in session_kwargs
        assert session_kwargs["metadata"]["user_id"] == str(self.user.id)
        assert "subscription_data" in session_kwargs
        assert session_kwargs["subscription_data"]["metadata"]["user_id"] == str(
            self.user.id
        )


class CustomerPortalViewTest(TestCase):
    """Tests for the customer portal view (subscription model only)."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="portal_user@example.com",
            password="testpass123",  # noqa: S106
            stripe_customer_id="cus_portal_user",
        )
        self.client = Client()
        self.client.force_login(self.user)
        self.portal_url = "/payments/customer-portal/"

    def test_portal_requires_login(self):
        """Test that customer portal requires authentication."""
        self.client.logout()
        response = self.client.get(self.portal_url)
        assert response.status_code == 302  # noqa: PLR2004
        assert "/accounts/login/" in response.url or "/login/" in response.url

    @patch("apps.payments.views.stripe.billing_portal.Session.create")
    @patch("apps.payments.views.stripe.Customer.retrieve")
    @override_settings(STRIPE_SECRET_KEY="sk_test_123")  # noqa: S106
    def test_portal_creates_session_and_redirects(
        self, mock_customer_retrieve, mock_portal_create
    ):
        """Test that portal creates billing session and redirects."""
        mock_customer_retrieve.return_value = {"id": "cus_portal_user"}
        mock_portal_create.return_value = MagicMock(
            url="https://billing.stripe.com/portal123"
        )

        response = self.client.get(self.portal_url)

        assert response.status_code == 303  # noqa: PLR2004
        mock_portal_create.assert_called_once()

        portal_kwargs = mock_portal_create.call_args[1]
        assert portal_kwargs["customer"] == "cus_portal_user"
        assert "return_url" in portal_kwargs

    @patch("apps.payments.views.stripe.Customer.retrieve")
    @override_settings(STRIPE_SECRET_KEY="sk_test_123")  # noqa: S106
    def test_portal_stripe_error_redirects_home(self, mock_customer_retrieve):
        """Test that Stripe error redirects to home."""
        mock_customer_retrieve.side_effect = StripeError("API Error")

        response = self.client.get(self.portal_url)

        assert response.status_code == 302  # noqa: PLR2004

    @override_settings(STRIPE_SECRET_KEY="")
    def test_portal_no_stripe_key_redirects_home(self):
        """Test that missing Stripe key redirects to home."""
        with patch("apps.payments.views.stripe_api_key", ""):
            response = self.client.get(self.portal_url)
            assert response.status_code == 302  # noqa: PLR2004
