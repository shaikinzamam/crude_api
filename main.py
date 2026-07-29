import sqlite3
from contextlib import closing

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


app = FastAPI(
    title="Task CRUD API",
    description="A FastAPI CRUD application using SQLite",
    version="2.0.0",
)

DATABASE_NAME = "tasks.db"


class TaskCreate(BaseModel):
    # No min_length here on purpose — Pydantic would reject an empty/missing
    # title with a 422 before our code ever runs. We validate manually below
    # so empty titles correctly return the 400 the assignment requires.
    title: str = ""


class TaskUpdate(BaseModel):
    title: str = ""
    done: bool = False


class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Make every HTTPException come back as {"error": "..."} instead of
    FastAPI's default {"detail": "..."}, matching the assignment spec.
    """

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


def get_database_connection() -> sqlite3.Connection:
    """
    Create and return a connection to the SQLite database.
    """

    connection = sqlite3.connect(DATABASE_NAME)

    # This allows rows to behave like dictionaries.
    connection.row_factory = sqlite3.Row

    return connection


def row_to_task(row: sqlite3.Row) -> dict:
    """
    Convert a SQLite row into the API response format.
    """

    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }


def initialize_database() -> None:
    """
    Create the tasks table and seed three tasks only when empty.
    """

    with closing(get_database_connection()) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        cursor.execute("SELECT COUNT(*) AS total FROM tasks")
        result = cursor.fetchone()

        if result["total"] == 0:
            example_tasks = [
                ("Learn FastAPI", 0),
                ("Connect API to SQLite", 0),
                ("Complete FlyRank assignment", 0),
            ]

            cursor.executemany(
                """
                INSERT INTO tasks (title, done)
                VALUES (?, ?)
                """,
                example_tasks,
            )

        connection.commit()


initialize_database()


@app.get("/")
def home():
    return {
        "message": "Task CRUD API is running",
        "database": DATABASE_NAME,
    }


@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks():
    with closing(get_database_connection()) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, title, done
            FROM tasks
            ORDER BY id
            """
        )

        rows = cursor.fetchall()

    return [row_to_task(row) for row in rows]


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    with closing(get_database_connection()) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, title, done
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        )

        row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return row_to_task(row)


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(task: TaskCreate):
    clean_title = task.title.strip()

    if not clean_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title is required",
        )

    with closing(get_database_connection()) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO tasks (title, done)
            VALUES (?, ?)
            """,
            (clean_title, 0),
        )

        task_id = cursor.lastrowid
        connection.commit()

        cursor.execute(
            """
            SELECT id, title, done
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        )

        row = cursor.fetchone()

    return row_to_task(row)


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskUpdate):
    clean_title = task.title.strip()

    if not clean_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title is required",
        )

    with closing(get_database_connection()) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        )

        existing_task = cursor.fetchone()

        if existing_task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        cursor.execute(
            """
            UPDATE tasks
            SET title = ?, done = ?
            WHERE id = ?
            """,
            (clean_title, int(task.done), task_id),
        )

        connection.commit()

        cursor.execute(
            """
            SELECT id, title, done
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        )

        updated_task = cursor.fetchone()

    return row_to_task(updated_task)


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(task_id: int):
    with closing(get_database_connection()) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        )

        existing_task = cursor.fetchone()

        if existing_task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        cursor.execute(
            """
            DELETE FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        )

        connection.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)