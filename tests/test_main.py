from unittest.mock import MagicMock

from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def setup_function():
    main.repository = MagicMock()


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Task CRUD API is running",
        "database": "PostgreSQL",
    }


def test_get_tasks():
    main.repository.get_all.return_value = [
        {
            "id": 1,
            "title": "Learn Docker",
            "done": False,
        }
    ]

    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "title": "Learn Docker",
            "done": False,
        }
    ]


def test_get_task():
    main.repository.get_by_id.return_value = {
        "id": 1,
        "title": "Learn Docker",
        "done": False,
    }

    response = client.get("/tasks/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_unknown_task():
    main.repository.get_by_id.return_value = None

    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json() == {
        "error": "Task not found",
    }


def test_create_task():
    main.repository.create.return_value = {
        "id": 4,
        "title": "Test PostgreSQL",
        "done": False,
    }

    response = client.post(
        "/tasks",
        json={"title": "Test PostgreSQL"},
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 4,
        "title": "Test PostgreSQL",
        "done": False,
    }

    main.repository.create.assert_called_once_with(
        "Test PostgreSQL",
        False,
    )


def test_create_task_with_empty_title():
    response = client.post(
        "/tasks",
        json={"title": "   "},
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": "Title is required",
    }


def test_update_task():
    main.repository.update.return_value = {
        "id": 1,
        "title": "Updated task",
        "done": True,
    }

    response = client.put(
        "/tasks/1",
        json={
            "title": "Updated task",
            "done": True,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Updated task",
        "done": True,
    }


def test_update_unknown_task():
    main.repository.update.return_value = None

    response = client.put(
        "/tasks/999",
        json={
            "title": "Unknown task",
            "done": False,
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "error": "Task not found",
    }


def test_delete_task():
    main.repository.delete.return_value = True

    response = client.delete("/tasks/1")

    assert response.status_code == 204
    assert response.content == b""


def test_delete_unknown_task():
    main.repository.delete.return_value = False

    response = client.delete("/tasks/999")

    assert response.status_code == 404
    assert response.json() == {
        "error": "Task not found",
    }