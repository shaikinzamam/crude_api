import pytest
from fastapi.testclient import TestClient

from main import app, reset_tasks, tasks


@pytest.fixture(autouse=True)
def clear_state():
    reset_tasks()
    yield
    reset_tasks()


client = TestClient(app)


def test_root_and_health_endpoints():
    root = client.get("/")
    assert root.status_code == 200
    assert root.json()["name"] == "Task API"

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}


def test_list_and_get_single_task():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 3

    single = client.get("/tasks/1")
    assert single.status_code == 200
    assert single.json()["id"] == 1

    missing = client.get("/tasks/99")
    assert missing.status_code == 404
    assert missing.json() == {"error": "Task 99 not found"}


def test_create_task_validation_and_creation():
    created = client.post("/tasks", json={"title": "Buy milk"})
    assert created.status_code == 201
    assert created.json()["title"] == "Buy milk"
    assert created.json()["done"] is False

    invalid = client.post("/tasks", json={})
    assert invalid.status_code == 400
    assert "title" in invalid.json()["error"].lower()

    assert len(tasks) == 4


def test_update_and_delete_task():
    updated = client.put("/tasks/1", json={"done": True})
    assert updated.status_code == 200
    assert updated.json()["done"] is True

    invalid_update = client.put("/tasks/1", json={})
    assert invalid_update.status_code == 400

    deleted = client.delete("/tasks/1")
    assert deleted.status_code == 204
    assert deleted.content == b""

    missing_delete = client.delete("/tasks/99")
    assert missing_delete.status_code == 404
