import sqlite3
import pytest
from fastapi.testclient import TestClient

from main import app, DATABASE_NAME

client = TestClient(app)


def reset_database():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("DELETE FROM tasks")

    # AUTOINCREMENT keeps its own counter in sqlite_sequence and never reuses
    # an id, even after DELETE. Reset it here so every test run starts the
    # seeded tasks back at id 1 — otherwise ids keep climbing across runs.
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'tasks'")

    cursor.executemany(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        [
            ("Learn FastAPI", 0),
            ("Connect API to SQLite", 0),
            ("Complete FlyRank assignment", 0),
        ],
    )
    connection.commit()
    connection.close()


@pytest.fixture(autouse=True)
def clear_state():
    reset_database()
    yield
    reset_database()


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["database"] == "tasks.db"


def test_list_and_get_single_task():
    response = client.get("/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 3

    # Don't hardcode an id — use the id the API actually gave the first task.
    # This keeps the test correct no matter what the autoincrement counter
    # happens to be at.
    first_task_id = tasks[0]["id"]

    single = client.get(f"/tasks/{first_task_id}")
    assert single.status_code == 200
    assert single.json()["id"] == first_task_id

    missing = client.get("/tasks/999999")
    assert missing.status_code == 404
    assert missing.json() == {"error": "Task not found"}


def test_create_task_validation_and_creation():
    created = client.post("/tasks", json={"title": "Buy milk"})
    assert created.status_code == 201
    assert created.json()["title"] == "Buy milk"
    assert created.json()["done"] is False

    invalid_empty_body = client.post("/tasks", json={})
    assert invalid_empty_body.status_code == 400

    invalid_blank_title = client.post("/tasks", json={"title": "   "})
    assert invalid_blank_title.status_code == 400

    listing = client.get("/tasks")
    assert len(listing.json()) == 4


def test_update_and_delete_task():
    tasks = client.get("/tasks").json()
    task_id = tasks[0]["id"]

    updated = client.put(
        f"/tasks/{task_id}",
        json={"title": "Learn FastAPI", "done": True},
    )
    assert updated.status_code == 200
    assert updated.json()["done"] is True

    invalid_update = client.put(
        f"/tasks/{task_id}",
        json={"title": "", "done": True},
    )
    assert invalid_update.status_code == 400

    deleted = client.delete(f"/tasks/{task_id}")
    assert deleted.status_code == 204
    assert deleted.content == b""

    missing_delete = client.delete(f"/tasks/{task_id}")
    assert missing_delete.status_code == 404