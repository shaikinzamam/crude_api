# Task API

A small in-memory to-do list CRUD API built with Python and FastAPI.

## Run it

```bash
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Then open the API root at <http://localhost:8000/> or the interactive Swagger UI at <http://localhost:8000/docs>.

## Endpoints

| Method | Path | Description | Success | Errors |
| --- | --- | --- | --- | --- |
| GET | `/` | API info | 200 | - |
| GET | `/health` | Health check | 200 | - |
| GET | `/tasks` | List tasks (`?done=`, `?search=`) | 200 | - |
| GET | `/tasks/{task_id}` | Get one task | 200 | 404 |
| POST | `/tasks` | Create a task | 201 | 400 |
| PUT | `/tasks/{task_id}` | Update a task | 200 | 400, 404 |
| DELETE | `/tasks/{task_id}` | Delete a task | 204 | 404 |
| GET | `/stats` | Task counts (extra) | 200 | - |
| POST | `/reset` | Restore the seed tasks (extra) | 200 | - |

## Example

```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Created with curl","done":false}'
```

Full response captured during the curl test pass:

```http
HTTP/1.1 201 Created
date: Sat, 18 Jul 2026 06:43:45 GMT
server: uvicorn
content-length: 49
content-type: application/json

{"id":4,"title":"Created with curl","done":false}
```
