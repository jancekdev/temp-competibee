import logging
from datetime import UTC
from datetime import datetime

import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.html import escape
from ninja import NinjaAPI
from ninja import Schema
from pydantic import Field
from stripe import StripeError

from .models import Todo

api = NinjaAPI()
logger = logging.getLogger(__name__)


# EXAMPLE DATA
# can be safely deleted
# ############################################################


class TodoIn(Schema):
    title: str = Field(..., max_length=200)
    description: str = ""
    completed: bool = False


class TodoUpdate(Schema):
    title: str = Field(None, max_length=200)
    description: str = None
    completed: bool = None


# ############################################################


class SubscriptionInfo(Schema):
    """Subscription details fetched from Stripe."""

    status: str | None = None
    current_period_end: str | None = None
    cancel_at_period_end: bool = False


class UserOut(Schema):
    id: int
    email: str
    name: str
    has_membership: bool
    membership_paused: bool
    subscription: SubscriptionInfo | None = None

    @staticmethod
    def from_orm(user):
        subscription_info = None
        if settings.STRIPE_SECRET_KEY and getattr(user, "stripe_customer_id", None):
            try:
                subscriptions = stripe.Subscription.list(
                    customer=user.stripe_customer_id,
                    status="all",
                    limit=5,
                )
                active_sub = next(
                    (
                        sub
                        for sub in subscriptions.data
                        if sub.get("status") in {"active", "trialing", "past_due"}
                    ),
                    None,
                )
                if active_sub:
                    period_end = active_sub.get("current_period_end")
                    subscription_info = SubscriptionInfo(
                        status=active_sub.get("status"),
                        current_period_end=(
                            datetime.fromtimestamp(period_end, tz=UTC).isoformat()
                            if period_end
                            else None
                        ),
                        cancel_at_period_end=active_sub.get(
                            "cancel_at_period_end", False
                        ),
                    )
            except StripeError as exc:
                logger.debug(
                    "Unable to fetch Stripe subscription for user %s: %s", user.pk, exc
                )

        return UserOut(
            id=user.id,
            email=escape(user.email),
            name=escape(user.name or user.email.split("@")[0]),
            has_membership=getattr(user, "has_membership", False),
            membership_paused=getattr(user, "membership_paused", False),
            subscription=subscription_info,
        )


@api.get("/user/", response=UserOut)
@login_required
def get_current_user(request):
    return UserOut.from_orm(request.user)


class MessageOut(Schema):
    message: str


@api.post("/debug/cancel-access/", response=MessageOut)
@login_required
def debug_cancel_access(request):
    """Debug endpoint to cancel user access. Only available in DEBUG mode."""
    if not settings.DEBUG:
        return {"message": "Only available in debug mode"}

    user = request.user
    user.has_membership = False
    user.membership_paused = False
    user.save(update_fields=["has_membership", "membership_paused"])
    return {"message": "Access cancelled"}


# EXAMPLE DATA
# can be safely deleted
# ############################################################
class TodoOut(Schema):
    id: int
    title: str
    description: str
    completed: bool
    created_at: str
    updated_at: str

    @staticmethod
    def from_orm(todo):
        return TodoOut(
            id=todo.id,
            title=escape(todo.title),
            description=escape(todo.description),
            completed=todo.completed,
            created_at=todo.created_at.isoformat(),
            updated_at=todo.updated_at.isoformat(),
        )


@api.get("/todos/", response=list[TodoOut])
@login_required
def list_todos(request):
    todos = Todo.objects.filter(user=request.user)
    return [TodoOut.from_orm(todo) for todo in todos]


@api.post("/todos/", response={201: TodoOut})
@login_required
def create_todo(request, data: TodoIn):
    todo = Todo.objects.create(
        user=request.user,
        title=data.title,
        description=data.description,
        completed=data.completed,
    )
    return 201, TodoOut.from_orm(todo)


@api.get("/todos/{todo_id}/", response=TodoOut)
@login_required
def get_todo(request, todo_id: int):
    todo = get_object_or_404(Todo, id=todo_id, user=request.user)
    return TodoOut.from_orm(todo)


@api.put("/todos/{todo_id}/", response=TodoOut)
@login_required
def update_todo(request, todo_id: int, data: TodoUpdate):
    todo = get_object_or_404(Todo, id=todo_id, user=request.user)

    if data.title is not None:
        todo.title = data.title
    if data.description is not None:
        todo.description = data.description
    if data.completed is not None:
        todo.completed = data.completed

    todo.save()
    return TodoOut.from_orm(todo)


@api.delete("/todos/{todo_id}/", response={204: None})
@login_required
def delete_todo(request, todo_id: int):
    todo = get_object_or_404(Todo, id=todo_id, user=request.user)
    todo.delete()
    return 204, None


# ############################################################
