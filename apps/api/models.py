from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


# EXAMPLE DATA
# can be safely deleted, in case you decide to delete
# (don't need the todo functionality) then don't forget to run migrations
# ############################################################
class Todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="todos")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


# ############################################################
