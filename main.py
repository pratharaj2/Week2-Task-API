import sqlite3
from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse, Response

app = FastAPI()
DB_FILE = "tasks.db"


def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )
    """)
    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    if count == 0:
        with conn:
            conn.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                [("Learn SQLite", 0), ("Build CRUD API", 1), ("Push to GitHub", 0)],
            )
    conn.close()


init_db()


def to_task(row):
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


@app.get("/tasks")