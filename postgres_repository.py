import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")


def get_conn():
    return psycopg.connect(DATABASE_URL)


def init_db():
    conn = get_conn()

    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN NOT NULL DEFAULT FALSE
                )
            """)

            cur.execute("SELECT COUNT(*) FROM tasks")
            count = cur.fetchone()[0]

            if count == 0:
                cur.executemany(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                    [
                        ("Learn SQLite", False),
                        ("Build CRUD API", True),
                        ("Push to GitHub", False),
                    ],
                )

    conn.close()


def get_all_tasks():
    conn = get_conn()

    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, done FROM tasks")
            rows = cur.fetchall()

    conn.close()
    return rows


def get_task_by_id(task_id):
    conn = get_conn()

    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, done FROM tasks WHERE id = %s",
                (task_id,),
            )
            row = cur.fetchone()

    conn.close()
    return row


def create_task(title):
    conn = get_conn()

    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tasks (title, done)
                VALUES (%s, %s)
                RETURNING id, title, done
                """,
                (title, False),
            )
            row = cur.fetchone()

    conn.close()
    return row


def update_task(task_id, title, done):
    conn = get_conn()

    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE tasks
                SET title = %s, done = %s
                WHERE id = %s
                RETURNING id, title, done
                """,
                (title, done, task_id),
            )
            row = cur.fetchone()

    conn.close()
    return row


def delete_task(task_id):
    conn = get_conn()

    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM tasks WHERE id = %s",
                (task_id,),
            )
            deleted = cur.rowcount

    conn.close()
    return deleted