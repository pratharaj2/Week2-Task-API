
import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Body, Depends
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import create_client

from postgres_repository import (
    init_db,
    get_all_tasks,
    get_task_by_id,
    create_task,
    update_task,
    delete_task,
)

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Supabase environment variables are missing")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Task API with Supabase Authentication")
security = HTTPBearer(auto_error=False)


class AuthError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message


@app.exception_handler(AuthError)
async def auth_error_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message},
    )


def to_task(row):
    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2]),
    }


def safe_user(user):
    return {
        "id": str(user.id),
        "email": user.email,
        "created_at": str(user.created_at) if user.created_at else None,
    }


# Reusable authentication dependency
def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthError(401, "Access token required")

    token = credentials.credentials

    try:
        response = supabase.auth.get_user(token)
        user = response.user
    except Exception as e:
        print(f"SUPABASE TOKEN VERIFICATION ERROR: {type(e).__name__}: {e}")
        raise AuthError(401, "Invalid or expired token")

    if user is None:
        raise AuthError(401, "Invalid or expired token")

    return user


# Initialize PostgreSQL
init_db()


# Existing PostgreSQL CRUD routes
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

    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required"},
        )

    return to_task(create_task(title.strip()))


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

    if not isinstance(title, str) or not title.strip():
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

    row = update_task(task_id, title.strip(), new_done)
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


# Signup
@app.post("/auth/signup", status_code=201)
def signup(body: dict = Body(default=None)):
    body = body or {}
    email = body.get("email")
    password = body.get("password")

    if (
        not isinstance(email, str)
        or not email.strip()
        or not isinstance(password, str)
        or not password
    ):
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required"},
        )

    try:
        response = supabase.auth.sign_up({
            "email": email.strip(),
            "password": password,
        })

        user = response.user

        if user is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Unable to create account"},
            )

        return {
            "message": "Signup successful",
            "user": safe_user(user),
        }

    except Exception as e:
        print(f"SUPABASE SIGNUP ERROR: {type(e).__name__}: {e}")
        return JSONResponse(
            status_code=400,
            content={"error": "Signup failed. Check server terminal."},
        )


# Login
@app.post("/auth/login", status_code=200)
def login(body: dict = Body(default=None)):
    body = body or {}
    email = body.get("email")
    password = body.get("password")

    if (
        not isinstance(email, str)
        or not email.strip()
        or not isinstance(password, str)
        or not password
    ):
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required"},
        )

    try:
        response = supabase.auth.sign_in_with_password({
            "email": email.strip(),
            "password": password,
        })

        session = response.session

        if session is None:
            print("SUPABASE LOGIN ERROR: No session returned")
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid login credentials"},
            )

        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "token_type": "bearer",
        }

    except Exception as e:
        # Diagnostic only: do not print passwords or tokens.
        print(f"SUPABASE LOGIN ERROR: {type(e).__name__}: {e}")
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid login credentials"},
        )


# Public route
@app.get("/public/info")
def public_info():
    return {
        "message": "Welcome stranger! This info is public."
    }


# Protected profile
@app.get("/protected/profile")
def protected_profile(
    current_user=Depends(get_current_user),
):
    return safe_user(current_user)


# Second protected route
@app.get("/protected/dashboard")
def protected_dashboard(
    current_user=Depends(get_current_user),
):
    return {
        "message": "Welcome to your protected dashboard",
        "user": safe_user(current_user),
    }


# Logout
@app.post("/auth/logout", status_code=204)
def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    current_user=Depends(get_current_user),
):
    token = credentials.credentials

    try:
        response = httpx.post(
            f"{SUPABASE_URL.rstrip('/')}/auth/v1/logout",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {token}",
            },
            timeout=10.0,
        )

        if response.status_code >= 400:
            print(f"Supabase logout returned HTTP {response.status_code}")
            return JSONResponse(
                status_code=502,
                content={"error": "Unable to log out from Supabase"},
            )

    except httpx.HTTPError as e:
        print(f"SUPABASE LOGOUT ERROR: {type(e).__name__}")
        return JSONResponse(
            status_code=502,
            content={"error": "Logout service unavailable"},
        )

    return Response(status_code=204)