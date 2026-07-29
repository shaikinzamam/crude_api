# FastAPI SQLite Task API

A persistent to-do list CRUD API built with Python, FastAPI, and SQLite.

This project upgrades the original in-memory CRUD API by storing tasks in a real SQLite database. The API endpoints remain the same, but tasks now survive server restarts.

## Why SQLite?

SQLite was chosen because:

- It requires no separate database server.
- It stores data in a single file.
- Python includes SQLite support through the built-in `sqlite3` library.
- It is simple to set up and suitable for small applications.
- Data remains available after the server restarts.

## Database

The application automatically creates:

```text
tasks.db