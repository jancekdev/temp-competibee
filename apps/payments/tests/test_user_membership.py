"""Tests for user membership and payment status fields."""

from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class SubscriptionUserFieldsTest(TestCase):
    """Tests for subscription-based user membership fields."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="member@example.com",
            password="testpass123",  # noqa: S106
        )

    def test_new_user_has_no_membership(self):
        """Test that new users don't have membership by default."""
        assert self.user.has_membership is False
        assert self.user.membership_paused is False

    def test_is_member_returns_true_when_active(self):
        """Test that is_member returns True when has_membership and not paused."""
        self.user.has_membership = True
        self.user.membership_paused = False
        self.user.save()

        assert self.user.is_member() is True

    def test_is_member_returns_false_when_paused(self):
        """Test that is_member returns False when membership is paused."""
        self.user.has_membership = True
        self.user.membership_paused = True
        self.user.save()

        assert self.user.is_member() is False

    def test_is_member_returns_false_when_no_membership(self):
        """Test that is_member returns False when has_membership is False."""
        self.user.has_membership = False
        self.user.membership_paused = False
        self.user.save()

        assert self.user.is_member() is False

    def test_stripe_customer_id_initially_empty(self):
        """Test that stripe_customer_id is empty by default."""
        assert self.user.stripe_customer_id == ""

    def test_stripe_customer_id_can_be_set(self):
        """Test that stripe_customer_id can be assigned."""
        self.user.stripe_customer_id = "cus_test123"
        self.user.save()

        self.user.refresh_from_db()
        assert self.user.stripe_customer_id == "cus_test123"

    def test_membership_transitions(self):
        """Test various membership state transitions."""
        assert self.user.is_member() is False

        self.user.has_membership = True
        self.user.save()
        assert self.user.is_member() is True

        self.user.membership_paused = True
        self.user.save()
        assert self.user.is_member() is False

        self.user.membership_paused = False
        self.user.save()
        assert self.user.is_member() is True

        self.user.has_membership = False
        self.user.save()
        assert self.user.is_member() is False


class StripeCustomerIdTest(TestCase):
    """Tests for stripe_customer_id field common to both models."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="stripe_user@example.com",
            password="testpass123",  # noqa: S106
        )

    def test_stripe_customer_id_max_length(self):
        """Test that stripe_customer_id accepts long IDs."""
        long_id = "cus_" + "a" * 200
        self.user.stripe_customer_id = long_id
        self.user.save()

        self.user.refresh_from_db()
        assert self.user.stripe_customer_id == long_id

    def test_multiple_users_can_have_same_empty_stripe_id(self):
        """Test that multiple users can have empty stripe_customer_id."""
        user2 = User.objects.create_user(
            email="another@example.com",
            password="testpass123",  # noqa: S106
        )

        assert self.user.stripe_customer_id == ""
        assert user2.stripe_customer_id == ""

    def test_stripe_customer_id_uniqueness_not_enforced(self):
        """Test that stripe_customer_id doesn't enforce uniqueness at DB level."""
        self.user.stripe_customer_id = "cus_shared"
        self.user.save()

        user2 = User.objects.create_user(
            email="another@example.com",
            password="testpass123",  # noqa: S106
            stripe_customer_id="cus_unique",
        )

        assert self.user.stripe_customer_id == "cus_shared"
        assert user2.stripe_customer_id == "cus_unique"
