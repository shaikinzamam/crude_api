# Task CRUD API — FastAPI, PostgreSQL, and Docker

A containerized Task CRUD API built with FastAPI and PostgreSQL.

This project was completed for the FlyRank Backend AI Engineering assignment **BE-04: Containerize Your Stack**. The API and database start together with one Docker Compose command, and PostgreSQL data persists across container restarts using a named Docker volume.

## Features

- FastAPI REST API
- PostgreSQL database
- Dockerized API and database
- One-command startup with Docker Compose
- Persistent database storage using a Docker volume
- Environment-based configuration with `.env`
- Repository pattern for database operations
- Parameterized SQL queries
- Automatic table creation and first-run seed data
- Correct CRUD status codes and error responses
- Automated route tests with pytest

## Architecture

```
Client / Swagger UI
        |
        v
FastAPI Routes
        |
        v
PostgresTaskRepository
        |
        v
PostgreSQL Container
        |
        v
Docker Named Volume
```

The previous version of this project used SQLite. For BE-04, SQLite was replaced with a PostgreSQL repository.

The API routes, validation rules, response structures, and status codes remain the same. Database operations are isolated inside `repository.py`.

## Project Structure

```
.
├── screenshots/
│   ├── create-task-201.png
│   ├── docker-containers.png
│   ├── persistence-after-restart.png
│   ├── postgres-data.png
│   ├── swagger-postgres.png
│   └── tests-passed.png
├── tests/
│   └── test_main.py
├── .dockerignore
├── .env.example
├── .gitignore
├── compose.yaml
├── Dockerfile
├── init.sql
├── main.py
├── pytest.ini
├── repository.py
├── requirements.txt
└── README.md
```

## Requirements

Install:

- Docker Desktop
- Git

You do not need to install PostgreSQL directly because it runs inside Docker.

## Environment Setup

Create your local `.env` file from `.env.example`.

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
```

Example variables:

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=dev
POSTGRES_DB=tasks
DATABASE_URL=postgresql://postgres:dev@localhost:5432/tasks
```

The real `.env` file is ignored by Git and must not be committed.

## Run the Full Stack

Start the FastAPI app and PostgreSQL database:

```bash
docker compose up --build
```

To run in the background:

```bash
docker compose up -d --build
```

Open Swagger UI:

```
http://localhost:8000/docs
```

Check running containers:

```bash
docker ps
```

Expected containers:

- `crud-api`
- `crud-postgres`

## API Endpoints

| Method | Endpoint | Description | Success Status |
|---|---|---|---|
| GET | `/` | API status message | 200 OK |
| GET | `/tasks` | Get all tasks | 200 OK |
| GET | `/tasks/{task_id}` | Get one task | 200 OK |
| POST | `/tasks` | Create a task | 201 Created |
| PUT | `/tasks/{task_id}` | Update a task | 200 OK |
| DELETE | `/tasks/{task_id}` | Delete a task | 204 No Content |

Additional responses:

- Empty or whitespace-only title: `400 Bad Request`
- Unknown task ID: `404 Not Found`

Error format:

```json
{
  "error": "Task not found"
}
```

## Example Requests

**Get all tasks**

```powershell
curl.exe -i http://localhost:8000/tasks
```

**Create a task**

```powershell
curl.exe -i -X POST http://localhost:8000/tasks `
  -H "Content-Type: application/json" `
  -d "{\"title\":\"Test Docker persistence\"}"
```

Example response:

```json
{
  "id": 4,
  "title": "Test Docker persistence",
  "done": false
}
```

**Update a task**

```powershell
curl.exe -i -X PUT http://localhost:8000/tasks/4 `
  -H "Content-Type: application/json" `
  -d "{\"title\":\"Test Docker persistence\",\"done\":true}"
```

**Delete a task**

```powershell
curl.exe -i -X DELETE http://localhost:8000/tasks/4
```

## Database Initialization

The `init.sql` file automatically:

- Creates the `tasks` table if it does not exist.
- Seeds three example tasks only when the table is empty.

Initial tasks:

1. Learn Docker
2. Connect FastAPI to PostgreSQL
3. Prove database persistence

## PostgreSQL Verification

View the stored rows directly inside PostgreSQL:

```bash
docker exec -it crud-postgres psql -U postgres -d tasks -c "SELECT * FROM tasks ORDER BY id;"
```

Example output:

```
 id |             title             | done
----+-------------------------------+------
  1 | Learn Docker                  | f
  2 | Connect FastAPI to PostgreSQL | f
  3 | Prove database persistence    | f
  4 | Test Docker persistence       | f
```

## Persistence Proof

Persistence was tested with this process:

1. Started the stack with `docker compose up -d`.
2. Created the task `Test Docker persistence`.
3. Confirmed the row inside PostgreSQL.
4. Stopped and removed the containers using:

   ```bash
   docker compose down
   ```

5. Restarted the stack using:

   ```bash
   docker compose up -d
   ```

6. Queried PostgreSQL again.
7. The same task was still present.

The data survived because PostgreSQL stores its files in the named Docker volume `taskdata`.

> Do not run the following command unless you intentionally want to delete the database data:
>
> ```bash
> docker compose down -v
> ```

## Run Tests

Run:

```bash
pytest -v
```

Current result:

```
10 passed
```

The tests mock the repository layer so route behavior can be tested without modifying the real PostgreSQL data.

## Screenshots

- Swagger UI
- Create Task — 201 Created
- PostgreSQL Data
- Persistence After Restart
- Running Docker Containers
- Tests Passed

## Stop the Stack

```bash
docker compose down
```

The named volume remains available, so the stored rows will still exist the next time the stack starts.

## Assignment Requirements Completed

- PostgreSQL runs in Docker
- PostgreSQL uses a named volume
- FastAPI and PostgreSQL start with `docker compose up`
- Database configuration comes from environment variables
- `.env` is ignored by Git
- `.env.example` is committed
- PostgreSQL repository replaces SQLite storage
- Routes and API behavior remain unchanged
- Parameterized SQL queries are used
- CRUD endpoints work correctly
- Persistence is proven across container restarts
- Automated tests pass
- Screenshots are included

## Author

**Shaik Inzamam**
GitHub: [shaikinzamam](https://github.com/shaikinzamam)
