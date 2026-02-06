from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.api.models import Todo

User = get_user_model()


class TodoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",  # noqa: S106
        )

    def test_todo_creation(self):
        todo = Todo.objects.create(
            user=self.user, title="Test Todo", description="Test Description"
        )
        assert todo.title == "Test Todo"
        assert todo.description == "Test Description"
        assert todo.completed is False
        assert todo.user == self.user

    def test_todo_str_representation(self):
        todo = Todo.objects.create(user=self.user, title="Test Todo")
        assert str(todo) == "Test Todo"

    def test_todo_ordering(self):
        todo1 = Todo.objects.create(user=self.user, title="First Todo")
        todo2 = Todo.objects.create(user=self.user, title="Second Todo")
        todos = Todo.objects.all()
        assert todos[0] == todo2
        assert todos[1] == todo1


class TodoAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",  # noqa: S106
        )
        self.client.force_login(self.user)

    def test_list_todos(self):
        Todo.objects.create(user=self.user, title="Todo 1")
        Todo.objects.create(user=self.user, title="Todo 2")
        response = self.client.get("/api/todos/")
        assert response.status_code == 200  # noqa: PLR2004
        data = response.json()
        assert len(data) == 2  # noqa: PLR2004

    def test_create_todo(self):
        response = self.client.post(
            "/api/todos/",
            data={"title": "New Todo", "description": "New Description"},
            content_type="application/json",
        )
        assert response.status_code == 201  # noqa: PLR2004
        assert Todo.objects.count() == 1
        todo = Todo.objects.first()
        assert todo.title == "New Todo"

    def test_get_todo_detail(self):
        todo = Todo.objects.create(user=self.user, title="Test Todo")
        response = self.client.get(f"/api/todos/{todo.id}/")
        assert response.status_code == 200  # noqa: PLR2004
        data = response.json()
        assert data["title"] == "Test Todo"

    def test_update_todo(self):
        todo = Todo.objects.create(user=self.user, title="Old Title")
        response = self.client.put(
            f"/api/todos/{todo.id}/",
            data={"title": "New Title", "completed": True},
            content_type="application/json",
        )
        assert response.status_code == 200  # noqa: PLR2004
        todo.refresh_from_db()
        assert todo.title == "New Title"
        assert todo.completed is True

    def test_delete_todo(self):
        todo = Todo.objects.create(user=self.user, title="To Delete")
        response = self.client.delete(f"/api/todos/{todo.id}/")
        assert response.status_code == 204  # noqa: PLR2004
        assert Todo.objects.count() == 0

    def test_user_can_only_see_own_todos(self):
        other_user = User.objects.create_user(
            email="other@example.com",
            password="otherpass123",  # noqa: S106
        )
        Todo.objects.create(user=self.user, title="My Todo")
        Todo.objects.create(user=other_user, title="Other Todo")
        response = self.client.get("/api/todos/")
        assert response.status_code == 200  # noqa: PLR2004
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "My Todo"
