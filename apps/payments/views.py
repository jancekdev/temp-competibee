import json
import logging
from collections.abc import Iterable
from typing import Any

import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from stripe import InvalidRequestError
from stripe import SignatureVerificationError
from stripe import StripeError

User = get_user_model()

logger = logging.getLogger(__name__)

stripe_api_key = settings.STRIPE_SECRET_KEY or settings.STRIPE_TEST_SECRET_KEY
if stripe_api_key:
    stripe.api_key = stripe_api_key
else:
    logger.warning("Stripe secret key is not configured; payment operations will fail.")

if settings.STRIPE_API_VERSION:
    stripe.api_version = settings.STRIPE_API_VERSION

SUBSCRIBER_METADATA_KEY = settings.STRIPE_SUBSCRIBER_METADATA_KEY
CHECKOUT_MODE = "subscription"


def _set_user_fields(user: User, **fields: Any) -> Iterable[str]:
    """Update model fields if values changed and return the list of updated fields."""
    changed = []
    for name, value in fields.items():
        if not hasattr(user, name):
            continue
        if getattr(user, name) != value:
            setattr(user, name, value)
            changed.append(name)
    if changed:
        user.save(update_fields=changed)
    return changed


def _link_user_to_customer(user: User, customer_id: str | None) -> None:
    if not customer_id:
        return
    updated = _set_user_fields(user, stripe_customer_id=customer_id)
    if updated:
        try:
            stripe.Customer.modify(
                customer_id,
                metadata={SUBSCRIBER_METADATA_KEY: str(user.pk)},
            )
        except StripeError as exc:
            logger.debug(
                "Unable to sync metadata for customer %s: %s", customer_id, exc
            )


def _get_or_create_customer_id(user: User) -> str:
    if user.stripe_customer_id:
        try:
            stripe.Customer.retrieve(user.stripe_customer_id)
        except InvalidRequestError:
            logger.info(
                "Stored Stripe customer %s was not found; creating a new one.",
                user.stripe_customer_id,
            )
            _set_user_fields(user, stripe_customer_id="")
        else:
            return user.stripe_customer_id

    metadata = {SUBSCRIBER_METADATA_KEY: str(user.pk)}
    try:
        customer = stripe.Customer.create(
            email=user.email,
            name=user.name or None,
            metadata=metadata,
        )
    except StripeError:
        logger.exception("Unable to create Stripe customer for user %s", user.pk)
        raise

    _set_user_fields(user, stripe_customer_id=customer["id"])
    return customer["id"]


def _get_user_for_customer(customer_id: str) -> User | None:
    if not customer_id:
        return None

    try:
        return User.objects.select_for_update().get(stripe_customer_id=customer_id)
    except User.DoesNotExist:
        try:
            customer = stripe.Customer.retrieve(customer_id)
        except StripeError as exc:
            logger.warning(
                "Customer %s not found when handling webhook: %s", customer_id, exc
            )
            return None

        metadata_user_id = customer.get("metadata", {}).get(SUBSCRIBER_METADATA_KEY)
        if not metadata_user_id:
            logger.warning(
                "Customer %s missing %s metadata", customer_id, SUBSCRIBER_METADATA_KEY
            )
            return None

        try:
            user = User.objects.select_for_update().get(pk=metadata_user_id)
        except User.DoesNotExist:
            logger.warning(
                "User %s referenced by customer %s does not exist",
                metadata_user_id,
                customer_id,
            )
            return None

        _link_user_to_customer(user, customer_id)
        return user


def _resolve_customer_from_charge(charge_id: str | None) -> str | None:
    if not charge_id:
        return None
    try:
        charge = stripe.Charge.retrieve(charge_id)
    except StripeError as exc:
        logger.warning("Unable to retrieve charge %s: %s", charge_id, exc)
        return None

    return charge.get("customer")


@login_required
def create_checkout_session(request, price_id):
    user = request.user

    if not stripe_api_key:
        logger.error(
            "Stripe secret key missing while attempting to create checkout session"
        )
        return HttpResponse("Stripe is not configured.", status=500)

    try:
        customer_id = _get_or_create_customer_id(user)
        stripe.Price.retrieve(price_id)

        metadata = {SUBSCRIBER_METADATA_KEY: str(user.id)}
        frontend_url = settings.FRONTEND_URL
        success_url = f"{frontend_url}/payments/success"
        cancel_url = f"{frontend_url}/payments/cancel"
        session_kwargs: dict[str, Any] = {
            "customer": customer_id,
            "line_items": [
                {
                    "price": price_id,
                    "quantity": 1,
                },
            ],
            "mode": CHECKOUT_MODE,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": metadata,
        }
        session_kwargs["subscription_data"] = {
            "metadata": metadata,
            "trial_period_days": 7,
        }

        checkout_session = stripe.checkout.Session.create(**session_kwargs)
        return HttpResponseRedirect(checkout_session.url, status=303)

    except InvalidRequestError:
        logger.exception("Stripe price lookup failed")
        return HttpResponse(
            "Invalid price ID. Please verify the configured prices.", status=400
        )
    except StripeError:
        logger.exception("Stripe API error creating checkout session")
        return HttpResponse(
            "We could not start the checkout session. Please try again.", status=400
        )
    except Exception:
        logger.exception("Unexpected error creating checkout session")
        return HttpResponse("Unexpected error. Please contact support.", status=500)


@login_required
def customer_portal(request):
    frontend_url = settings.FRONTEND_URL
    return_url = f"{frontend_url}/app"
    user = request.user

    if not stripe_api_key:
        logger.error(
            "Stripe secret key missing while attempting to open customer portal"
        )
        return redirect(frontend_url)

    try:
        customer_id = _get_or_create_customer_id(user)
        portal_session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return HttpResponseRedirect(portal_session.url, status=303)

    except StripeError:
        logger.exception("Stripe API error creating portal session")
        return redirect(frontend_url)
    except Exception:
        logger.exception("Unexpected error creating portal session")
        return redirect(frontend_url)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        if settings.STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=settings.STRIPE_WEBHOOK_SECRET,
            )
        else:
            event = stripe.Event.construct_from(
                json.loads(payload.decode("utf-8")), stripe.api_key
            )
    except ValueError:
        logger.warning("Invalid payload for Stripe webhook")
        return HttpResponse(status=400)
    except SignatureVerificationError:
        logger.warning("Invalid signature for Stripe webhook")
        return HttpResponse(status=400)
    except StripeError as exc:
        logger.warning("Stripe error validating webhook: %s", exc)
        return HttpResponse(status=400)

    _dispatch_webhook(event)
    return HttpResponse(status=200)


def _dispatch_webhook(event):
    event_type = event.get("type")
    data_object = event.get("data", {}).get("object", {})

    if event_type in {
        "checkout.session.completed",
        "checkout.session.async_payment_succeeded",
    }:
        _handle_checkout_session(data_object)
    elif event_type == "customer.subscription.deleted":
        _handle_subscription_deleted(data_object)
    elif event_type == "customer.subscription.updated":
        _handle_subscription_updated(data_object)
    elif event_type == "customer.subscription.paused":
        _handle_subscription_paused(data_object)
    elif event_type == "customer.subscription.resumed":
        _handle_subscription_resumed(data_object)
    elif event_type == "charge.dispute.created":
        _handle_subscription_dispute_created(data_object)
    elif event_type == "invoice.upcoming":
        _handle_invoice_upcoming(data_object)
    else:
        logger.debug("Unhandled Stripe event: %s", event_type)


def _handle_checkout_session(session: dict[str, Any]):
    user_id = (session.get("metadata") or {}).get(SUBSCRIBER_METADATA_KEY)
    if not user_id:
        logger.warning("Checkout session %s missing user metadata", session.get("id"))
        return

    try:
        with transaction.atomic():
            user = User.objects.select_for_update().get(pk=user_id)
            _link_user_to_customer(user, session.get("customer"))
            _set_user_fields(user, has_membership=True, membership_paused=False)
    except User.DoesNotExist:
        logger.exception("User %s not found for checkout session", user_id)
    except Exception:
        logger.exception("Error handling checkout session %s", session.get("id"))


def _handle_subscription_deleted(subscription: dict[str, Any]):
    customer_id = subscription.get("customer")
    if not customer_id:
        logger.warning("Subscription %s missing customer", subscription.get("id"))
        return

    with transaction.atomic():
        user = _get_user_for_customer(customer_id)
        if not user:
            logger.warning("No user linked to subscription customer %s", customer_id)
            return
        _set_user_fields(user, has_membership=False, membership_paused=False)


def _handle_subscription_updated(subscription: dict[str, Any]):
    customer_id = subscription.get("customer")
    status = subscription.get("status")
    if not customer_id or not status:
        logger.warning("Subscription update missing customer or status")
        return

    with transaction.atomic():
        user = _get_user_for_customer(customer_id)
        if not user:
            logger.warning("No user linked to subscription customer %s", customer_id)
            return

        if status in {"trialing", "active"}:
            _set_user_fields(user, has_membership=True, membership_paused=False)
        elif status in {"past_due", "unpaid"}:
            _set_user_fields(user, has_membership=True, membership_paused=True)
        elif status in {"canceled", "incomplete_expired"}:
            _set_user_fields(user, has_membership=False, membership_paused=False)
        elif status == "paused":
            _set_user_fields(user, has_membership=True, membership_paused=True)
        else:
            logger.info("Unhandled subscription status %s for user %s", status, user.pk)


def _handle_subscription_paused(subscription: dict[str, Any]):
    customer_id = subscription.get("customer")
    if not customer_id:
        return

    with transaction.atomic():
        user = _get_user_for_customer(customer_id)
        if user:
            _set_user_fields(user, membership_paused=True)


def _handle_subscription_resumed(subscription: dict[str, Any]):
    customer_id = subscription.get("customer")
    if not customer_id:
        return

    with transaction.atomic():
        user = _get_user_for_customer(customer_id)
        if user:
            _set_user_fields(user, membership_paused=False)


def _handle_subscription_dispute_created(dispute: dict[str, Any]):
    charge_id = dispute.get("charge")
    customer_id = dispute.get("customer") or _resolve_customer_from_charge(charge_id)
    if not customer_id:
        logger.warning("Dispute %s missing customer", dispute.get("id"))
        return

    with transaction.atomic():
        user = _get_user_for_customer(customer_id)
        if user:
            _set_user_fields(user, membership_paused=True)
            amount = (dispute.get("amount") or 0) / 100
            logger.warning(
                "Membership paused for user %s due to dispute on charge %s "
                "(amount %.2f)",
                user.pk,
                charge_id,
                amount,
            )


def _handle_invoice_upcoming(invoice: dict[str, Any]):
    customer_id = invoice.get("customer")
    if not customer_id:
        return

    with transaction.atomic():
        user = _get_user_for_customer(customer_id)
        if user:
            logger.info("Upcoming invoice for user %s", user.pk)
        else:
            logger.info("Upcoming invoice for customer %s", customer_id)
