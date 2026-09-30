from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import sqlite3


app = FastAPI(
    title="Task CRUD API",
    description="A simple CRUD API built with Python and FastAPI",
    version="1.0.0"
)


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    completed: bool = False


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


DATABASE = "tasks.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create database and table automatically
conn = get_db_connection()

conn.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL DEFAULT '',
        completed BOOLEAN NOT NULL DEFAULT 0
    )
""")

conn.commit()


# Insert 3 example tasks only if the table is empty
task_count = conn.execute(
    "SELECT COUNT(*) FROM tasks"
).fetchone()[0]

if task_count == 0:
    conn.executemany(
        """
        INSERT INTO tasks (title, description, completed)
        VALUES (?, ?, ?)
        """,
        [
            (
                "Learn FastAPI",
                "Build a CRUD API",
                0
            ),
            (
                "Learn SQLite",
                "Connect FastAPI to SQLite",
                0
            ),
            (
                "Test database",
                "Verify data persistence",
                0
            )
        ]
    )

    conn.commit()

conn.close()


@app.get("/")
def root():
    return {
        "message": "Task CRUD API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# GET all tasks
@app.get("/tasks")
def get_tasks():
    conn = get_db_connection()

    tasks = conn.execute(
        "SELECT * FROM tasks"
    ).fetchall()

    conn.close()

    return [dict(task) for task in tasks]


# GET one task
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_db_connection()

    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    conn.close()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    return dict(task)


# CREATE task
@app.post(
    "/tasks",
    status_code=status.HTTP_201_CREATED
)
def create_task(task: TaskCreate):

    if not task.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title cannot be empty"
        )

    conn = get_db_connection()

    cursor = conn.execute(
        """
        INSERT INTO tasks (
            title,
            description,
            completed
        )
        VALUES (?, ?, ?)
        """,
        (
            task.title,
            task.description,
            task.completed
        )
    )

    conn.commit()

    new_task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (cursor.lastrowid,)
    ).fetchone()

    conn.close()

    return dict(new_task)


# UPDATE task
@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    task_update: TaskUpdate
):

    # At least one field must be provided
    if (
        task_update.title is None
        and task_update.description is None
        and task_update.completed is None
    ):
        raise HTTPException(
            status_code=400,
            detail="At least one field is required"
        )

    conn = get_db_connection()

    # Find existing task
    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if task is None:
        conn.close()

        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    # Keep existing values
    title = task["title"]
    description = task["description"]
    completed = task["completed"]

    # Update title if provided
    if task_update.title is not None:

        if not task_update.title.strip():
            conn.close()

            raise HTTPException(
                status_code=400,
                detail="Title cannot be empty"
            )

        title = task_update.title

    # Update description if provided
    if task_update.description is not None:
        description = task_update.description

    # Update completed if provided
    if task_update.completed is not None:
        completed = task_update.completed

    # Save changes to database
    conn.execute(
        """
        UPDATE tasks
        SET
            title = ?,
            description = ?,
            completed = ?
        WHERE id = ?
        """,
        (
            title,
            description,
            completed,
            task_id
        )
    )

    conn.commit()

    # Get updated task
    updated_task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    conn.close()

    return dict(updated_task)


# DELETE task
@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_task(task_id: int):

    conn = get_db_connection()

    # Check whether task exists
    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if task is None:
        conn.close()

        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    # Delete task
    conn.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    conn.commit()
    conn.close()

    return