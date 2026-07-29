FastAPI SQLite Task CRUD API

A persistent task-management CRUD API built with Python, FastAPI, and SQLite.

This project upgrades the original in-memory CRUD API by storing tasks in a real SQLite database. The API endpoints remain the same, but tasks now survive server restarts.

Features

Create, read, update, and delete tasks

SQLite database persistence

Automatic database and table creation

Three example tasks inserted only when the database is empty

Request validation with 400 Bad Request

404 Not Found for unknown task IDs

Interactive API documentation with Swagger UI

Automated tests using pytest

Parameterized SQL queries

Why SQLite?

SQLite was chosen because:

It requires no separate database server.

It stores the complete database in a single file.

Python includes SQLite support through the built-in sqlite3 library.

It is simple to configure and suitable for small applications.

Data remains available after the FastAPI server restarts.

Project Structure

crude_api/
├── screenshots/
│   └── database-view.png
├── tests/
│   └── test_main.py
├── .gitignore
├── main.py
├── README.md
└── requirements.txt

The tasks.db file is created automatically when the application starts. It is excluded from Git so every cloned project can create a fresh local database.

Database Schema

The application creates a table named tasks:

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done INTEGER NOT NULL DEFAULT 0
);

Column

Type

Description

id

Integer

Unique task identifier

title

Text

Task title

done

Boolean/Integer

0 for incomplete and 1 for completed

Installation

1. Clone the repository

git clone https://github.com/shaikinzamam/crude_api.git
cd crude_api

2. Create a virtual environment

python -m venv .venv

Activate it on Windows PowerShell:

.\.venv\Scripts\Activate.ps1

3. Install dependencies

pip install -r requirements.txt

Run the Application

python -m uvicorn main:app --reload --port 8000

Open Swagger UI:

http://127.0.0.1:8000/docs

API Endpoints

Method

Endpoint

Description

Success code

GET

/

API information

200

GET

/tasks

Return all tasks

200

GET

/tasks/{task_id}

Return one task

200

POST

/tasks

Create a new task

201

PUT

/tasks/{task_id}

Update a task

200

DELETE

/tasks/{task_id}

Delete a task

204

Example Requests

Create a task

POST /tasks
Content-Type: application/json

{
  "title": "Learn SQLite"
}

Example response:

{
  "id": 4,
  "title": "Learn SQLite",
  "done": false
}

Update a task

PUT /tasks/4
Content-Type: application/json

{
  "title": "Complete SQLite assignment",
  "done": true
}

Delete a task

DELETE /tasks/4

A successful deletion returns 204 No Content.

Error Responses

Invalid request:

{
  "error": "Title is required"
}

Unknown task ID:

{
  "error": "Task not found"
}

SQL Queries Explored

List every task:

SELECT * FROM tasks;

Show only completed tasks:

SELECT * FROM tasks WHERE done = 1;

Count all tasks:

SELECT COUNT(*) FROM tasks;

Update all tasks as completed:

UPDATE tasks SET done = 1;

Delete all completed tasks:

DELETE FROM tasks WHERE done = 1;

Database Screenshot



Persistence Test

Create a new task using POST /tasks.

Stop the FastAPI server.

Start the server again.

Run GET /tasks.

The task remains available because it is stored in tasks.db instead of an in-memory Python list.

Run Tests

python -m pytest

Expected result:

4 passed

Technologies Used

Python

FastAPI

SQLite

Uvicorn

Pydantic

Pytest

DB Browser for SQLite

Assignment Outcome

The API contract stayed the same while the storage layer changed from an in-memory list to SQLite. This demonstrates an important backend-development principle:

The API describes what the application does, while the database determines where the application stores its data.

Author

Shaik Inzamam

GitHub: shaikinzamam
