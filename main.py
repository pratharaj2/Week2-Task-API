from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse, Response

from postgres_repository import (
    init_db,
    get_all_tasks,
    get_task_by_id,
    create_task,
    update_task,
    delete_task,
)


app = FastAPI()


def to_task(row):
    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2]),
    }


init_db()


@app.get("/tasks")
def get_tasks():
    rows = get_all_tasks()
    return [to_task(row) for row in rows]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    row = get_task_by_id(task_id)

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"},
        )

    return to_task(row)


@app.post("/tasks", status_code=201)
def create_task_endpoint(body: dict = Body(default=None)):
    title = (body or {}).get("title")

    if not isinstance(title, str) or title.strip() == "":
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required"},
        )

    row = create_task(title.strip())
    return to_task(row)


@app.put("/tasks/{task_id}")
def update_task_endpoint(
    task_id: int,
    body: dict = Body(default=None),
):
    existing = get_task_by_id(task_id)

    if existing is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"},
        )

    body = body or {}
    title = body.get("title")
    done = body.get("done")

    if not isinstance(title, str) or title.strip() == "":
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required"},
        )

    if done is not None and not isinstance(done, bool):
        return JSONResponse(
            status_code=400,
            content={"error": "done must be true or false"},
        )

    new_done = bool(existing[2]) if done is None else done

    row = update_task(
        task_id,
        title.strip(),
        new_done,
    )

    return to_task(row)


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task_endpoint(task_id: int):
    deleted = delete_task(task_id)

    if deleted == 0:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"},
        )

    return Response(status_code=204)