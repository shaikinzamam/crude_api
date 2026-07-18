from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A tiny in-memory to-do list API — the CRUD assignment.",
)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "title is required and cannot be empty"})


# ---------- Data models ----------

class Task(BaseModel):
    id: int
    title: str
    done: bool = False


class TaskCreate(BaseModel):
    title: str
    done: Optional[bool] = False


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


# ---------- In-memory "database" ----------

tasks: list[Task] = [
    Task(id=1, title="Buy milk", done=False),
    Task(id=2, title="Walk the dog", done=False),
    Task(id=3, title="Write README", done=True),
]
next_id = 4


def find_task(task_id: int) -> Task:
    for t in tasks:
        if t.id == task_id:
            return t
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


# ---------- Stage 1: root & health ----------

@app.get("/", summary="API info")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


# ---------- Stage 2: Read ----------

@app.get("/tasks", response_model=list[Task], summary="List all tasks")
def list_tasks(done: Optional[bool] = None, search: Optional[str] = None):
    """Optional query params: ?done=true / ?search=milk (extras, not required)."""
    result = tasks
    if done is not None:
        result = [t for t in result if t.done == done]
    if search:
        result = [t for t in result if search.lower() in t.title.lower()]
    return result


@app.get("/tasks/{task_id}", response_model=Task, summary="Get a single task")
def get_task(task_id: int):
    return find_task(task_id)


# ---------- Stage 3: Create ----------

@app.post("/tasks", response_model=Task, status_code=201, summary="Create a task")
def create_task(payload: TaskCreate):
    global next_id
    if not payload.title or not payload.title.strip():
        raise HTTPException(status_code=400, detail="title is required and cannot be empty")

    task = Task(id=next_id, title=payload.title.strip(), done=payload.done or False)
    tasks.append(task)
    next_id += 1
    return task


# ---------- Stage 4: Update & Delete ----------

@app.put("/tasks/{task_id}", response_model=Task, summary="Update a task")
def update_task(task_id: int, payload: TaskUpdate):
    task = find_task(task_id)

    if payload.title is None and payload.done is None:
        raise HTTPException(status_code=400, detail="provide at least one of: title, done")
    if payload.title is not None and not payload.title.strip():
        raise HTTPException(status_code=400, detail="title cannot be empty")

    if payload.title is not None:
        task.title = payload.title.strip()
    if payload.done is not None:
        task.done = payload.done
    return task


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    task = find_task(task_id)
    tasks.remove(task)
    return None


# ---------- Extras (optional) ----------

@app.get("/stats", summary="Task stats (extra)")
def stats():
    total = len(tasks)
    done_count = sum(1 for t in tasks if t.done)
    return {"total": total, "done": done_count, "open": total - done_count}


@app.post("/reset", summary="Reset to seed data (extra)")
def reset():
    global tasks, next_id
    tasks = [
        Task(id=1, title="Buy milk", done=False),
        Task(id=2, title="Walk the dog", done=False),
        Task(id=3, title="Write README", done=True),
    ]
    next_id = 4
    return {"status": "reset"}