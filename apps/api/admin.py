from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Todo


@admin.register(Todo)
class TodoAdmin(ModelAdmin):
    list_display = ("id", "title", "completed", "created_at")
    list_filter = ("completed",)
    search_fields = ("title", "description")
    ordering = ("-created_at",)
