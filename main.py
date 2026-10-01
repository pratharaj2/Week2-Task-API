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
@app.get("/tasks")
def get_tasks():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return [to_task(r) for r in rows]

@app.get("/tasks")
def get_tasks():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return [to_task(r) for r in rows]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_conn()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    if row is None:
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    return to_task(row)

@app.post("/tasks", status_code=201)
def create_task(body: dict = Body(default=None)):
    title = (body or {}).get("title")
    if not isinstance(title, str) or title.strip() == "":
        return JSONResponse(status_code=400, content={"error": "Title is required"})
    conn = get_conn()
    with conn:
        cur = conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (title.strip(), 0))
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (cur.lastrowid,)).fetchone()
    conn.close()
    return to_task(row)
@app.put("/tasks/{task_id}")
def update_task(task_id: int, body: dict = Body(default=None)):
    conn = get_conn()
    existing = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if existing is None:
        conn.close()
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    body = body or {}
    title = body.get("title")
    done = body.get("done")
    if not isinstance(title, str) or title.strip() == "":
        conn.close()
        return JSONResponse(status_code=400, content={"error": "Title is required"})
    if done is not None and not isinstance(done, bool):
        conn.close()
        return JSONResponse(status_code=400, content={"error": "done must be true or false"})
    new_done = existing["done"] if done is None else int(done)
    with conn:
        conn.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?",
                     (title.strip(), new_done, task_id))
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return to_task(row)


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    conn = get_conn()
    with conn:
        cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.close()
    if cur.rowcount == 0:
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    return Response(status_code=204)@app.get("/tasks")