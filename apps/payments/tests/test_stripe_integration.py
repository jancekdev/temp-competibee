"""Tests for Stripe customer management and core integration."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from stripe import InvalidRequestError
from stripe import StripeError

from apps.payments.views import _get_or_create_customer_id
from apps.payments.views import _get_user_for_customer
from apps.payments.views import _link_user_to_customer
from apps.payments.views import _resolve_customer_from_charge
from apps.payments.views import _set_user_fields

User = get_user_model()


class StripeCustomerManagementTest(TestCase):
    """Tests for Stripe customer creation and retrieval."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",  # noqa: S106
        )

    @patch("apps.payments.views.stripe.Customer.create")
    def test_create_new_customer_for_user_without_stripe_id(self, mock_create):
        """Test that new Stripe customer is created for users without stripe_id."""
        mock_create.return_value = {"id": "cus_new123"}

        customer_id = _get_or_create_customer_id(self.user)

        assert customer_id == "cus_new123"
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["email"] == "test@example.com"
        assert "metadata" in call_kwargs

        self.user.refresh_from_db()
        assert self.user.stripe_customer_id == "cus_new123"

    @patch("apps.payments.views.stripe.Customer.retrieve")
    def test_return_existing_customer_id_if_valid(self, mock_retrieve):
        """Test that existing valid customer ID is returned without creating new one."""
        self.user.stripe_customer_id = "cus_existing123"
        self.user.save()

        mock_retrieve.return_value = {"id": "cus_existing123"}

        customer_id = _get_or_create_customer_id(self.user)

        assert customer_id == "cus_existing123"
        mock_retrieve.assert_called_once_with("cus_existing123")

    @patch("apps.payments.views.stripe.Customer.create")
    @patch("apps.payments.views.stripe.Customer.retrieve")
    def test_create_new_customer_if_existing_id_invalid(
        self, mock_retrieve, mock_create
    ):
        """Test that a new customer is created if existing ID is invalid in Stripe."""
        self.user.stripe_customer_id = "cus_deleted123"
        self.user.save()

        mock_retrieve.side_effect = InvalidRequestError(
            message="No such customer", param="customer"
        )
        mock_create.return_value = {"id": "cus_new456"}

        customer_id = _get_or_create_customer_id(self.user)

        assert customer_id == "cus_new456"
        self.user.refresh_from_db()
        assert self.user.stripe_customer_id == "cus_new456"

    @patch("apps.payments.views.stripe.Customer.modify")
    def test_link_user_to_customer_updates_metadata(self, mock_modify):
        """Test that linking user to customer updates Stripe metadata."""
        _link_user_to_customer(self.user, "cus_link123")

        self.user.refresh_from_db()
        assert self.user.stripe_customer_id == "cus_link123"
        mock_modify.assert_called_once()

    def test_link_user_to_customer_with_none_id(self):
        """Test that linking with None customer_id does nothing."""
        original_id = self.user.stripe_customer_id
        _link_user_to_customer(self.user, None)

        self.user.refresh_from_db()
        assert self.user.stripe_customer_id == original_id


class GetUserForCustomerTest(TestCase):
    """Tests for resolving users from Stripe customer IDs."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="customer@example.com",
            password="testpass123",  # noqa: S106
            stripe_customer_id="cus_user123",
        )

    def test_get_user_by_stripe_customer_id(self):
        """Test that user can be found by stripe_customer_id."""
        user = _get_user_for_customer("cus_user123")
        assert user == self.user

    @patch("apps.payments.views.stripe.Customer.retrieve")
    def test_get_user_from_stripe_metadata_when_not_linked(self, mock_retrieve):
        """Test that user can be found via Stripe metadata when not directly linked."""
        new_user = User.objects.create_user(
            email="new@example.com",
            password="testpass123",  # noqa: S106
        )
        mock_retrieve.return_value = {
            "id": "cus_metadata123",
            "metadata": {"user_id": str(new_user.pk)},
        }

        user = _get_user_for_customer("cus_metadata123")

        assert user == new_user
        new_user.refresh_from_db()
        assert new_user.stripe_customer_id == "cus_metadata123"

    @patch("apps.payments.views.stripe.Customer.retrieve")
    def test_return_none_for_nonexistent_customer(self, mock_retrieve):
        """Test that None is returned when customer doesn't exist."""
        mock_retrieve.side_effect = StripeError("Customer not found")

        user = _get_user_for_customer("cus_nonexistent")
        assert user is None

    def test_return_none_for_empty_customer_id(self):
        """Test that None is returned for empty customer ID."""
        assert _get_user_for_customer("") is None
        assert _get_user_for_customer(None) is None


class SetUserFieldsTest(TestCase):
    """Tests for the _set_user_fields helper function."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="fields@example.com",
            password="testpass123",  # noqa: S106
        )

    def test_set_user_fields_updates_changed_values(self):
        """Test that only changed fields are updated."""
        changed = _set_user_fields(self.user, stripe_customer_id="cus_new")

        assert "stripe_customer_id" in changed
        self.user.refresh_from_db()
        assert self.user.stripe_customer_id == "cus_new"

    def test_set_user_fields_skips_unchanged_values(self):
        """Test that unchanged fields are not included in update."""
        self.user.stripe_customer_id = "cus_same"
        self.user.save()

        changed = _set_user_fields(self.user, stripe_customer_id="cus_same")

        assert len(changed) == 0

    def test_set_user_fields_ignores_nonexistent_fields(self):
        """Test that nonexistent field names are ignored."""
        changed = _set_user_fields(self.user, nonexistent_field="value")

        assert len(changed) == 0


class ResolveCustomerFromChargeTest(TestCase):
    """Tests for resolving customer ID from charge ID."""

    @patch("apps.payments.views.stripe.Charge.retrieve")
    def test_resolve_customer_from_valid_charge(self, mock_retrieve):
        """Test that customer ID is extracted from charge."""
        mock_retrieve.return_value = {"id": "ch_123", "customer": "cus_from_charge"}

        customer_id = _resolve_customer_from_charge("ch_123")

        assert customer_id == "cus_from_charge"
        mock_retrieve.assert_called_once_with("ch_123")

    @patch("apps.payments.views.stripe.Charge.retrieve")
    def test_return_none_for_charge_without_customer(self, mock_retrieve):
        """Test that None is returned when charge has no customer."""
        mock_retrieve.return_value = {"id": "ch_123", "customer": None}

        customer_id = _resolve_customer_from_charge("ch_123")

        assert customer_id is None

    @patch("apps.payments.views.stripe.Charge.retrieve")
    def test_return_none_for_stripe_error(self, mock_retrieve):
        """Test that None is returned on Stripe API error."""
        mock_retrieve.side_effect = StripeError("Charge not found")

        customer_id = _resolve_customer_from_charge("ch_invalid")

        assert customer_id is None

    def test_return_none_for_empty_charge_id(self):
        """Test that None is returned for empty charge ID."""
        assert _resolve_customer_from_charge(None) is None
        assert _resolve_customer_from_charge("") is None
