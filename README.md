# Task CRUD API

A REST API built with Python, FastAPI, and PostgreSQL. This project started as an in-memory task API, moved to SQLite in A2, and now runs against PostgreSQL in Docker with persistent storage.

## Project Purpose

This project demonstrates a complete CRUD API running against a real PostgreSQL database in a Dockerized environment.

The storage layer was swapped from SQLite to PostgreSQL while keeping the API routes and endpoint behaviour unchanged. Database access is kept in the PostgreSQL repository module.

## Tech Stack

* Python 3.12
* FastAPI
* Pydantic
* Uvicorn
* PostgreSQL 17
* psycopg
* Docker
* Docker Compose

## Features

* Create tasks
* Read all tasks
* Read a single task
* Update tasks
* Delete tasks
* Input validation
* 404 error handling
* PostgreSQL persistence
* Dockerized PostgreSQL database
* Docker Compose for the complete stack
* Persistent Docker volume
* Environment-based database configuration
* Parameterized SQL queries
* Health check endpoint
* Interactive Swagger documentation

## Architecture

The API routes communicate with the PostgreSQL repository instead of accessing the database directly.

```text
Client
  |
  v
FastAPI Routes
  |
  v
PostgreSQL Repository
  |
  v
PostgreSQL
  |
  v
Docker Volume
```

The service and route behaviour remains unchanged while the storage implementation is PostgreSQL.

## API Endpoints

| Method | Endpoint           | Description   | Success |
| ------ | ------------------ | ------------- | ------- |
| GET    | `/`                | API status    | 200     |
| GET    | `/health`          | Health check  | 200     |
| GET    | `/tasks`           | Get all tasks | 200     |
| GET    | `/tasks/{task_id}` | Get one task  | 200     |
| POST   | `/tasks`           | Create a task | 201     |
| PUT    | `/tasks/{task_id}` | Update a task | 200     |
| DELETE | `/tasks/{task_id}` | Delete a task | 204     |

Unknown task IDs return `404`. Invalid task data returns `400`.

## Environment Configuration

The database connection string is provided through the `DATABASE_URL` environment variable.

The real `.env` file is git-ignored and is not committed to the repository.

Create `.env` from the example:

```bash
cp .env.example .env
```

Then set the database connection string:

```env
DATABASE_URL=postgres://postgres:dev@db:5432/tasks
```

For PowerShell, you can also create `.env` manually using the same value.

`.env.example` is committed to the repository as a template.

## Run the Complete Stack

Docker Desktop must be running.

Start the API and PostgreSQL database together:

```bash
docker compose up
```

Or run in detached mode:

```bash
docker compose up -d
```

Check the running services:

```bash
docker compose ps
```

The API is available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Database

PostgreSQL runs in a Docker container using the official PostgreSQL image.

The database uses a named Docker volume:

```yaml
taskdata:/var/lib/postgresql/data
```

This volume keeps PostgreSQL data available when the containers are stopped and recreated.

The `tasks` table is created automatically if it does not already exist, and the initial example tasks are seeded only when the table is empty.

## PostgreSQL Verification

The database table was verified directly inside the PostgreSQL container:

```text
docker compose exec db psql -U postgres -d tasks -c "\dt"

         List of relations
 Schema | Name  | Type  |  Owner
--------+-------+-------+----------
 public | tasks | table | postgres
(1 row)
```

The stored rows were verified with:

```text
docker compose exec db psql -U postgres -d tasks -c "SELECT * FROM tasks;"

 id |     title      | done
----+----------------+------
  1 | Learn SQLite   | f
  2 | Build CRUD API | t
  3 | Push to GitHub | f
(3 rows)
```

## CRUD Verification

Example request:

```bash
curl -i http://127.0.0.1:8000/tasks
```

Expected response:

```text
HTTP/1.1 200 OK
```

The response contains the tasks stored in PostgreSQL.

The CRUD flow was also tested with:

* `GET /tasks` → `200`
* `GET /tasks/{id}` → `200`
* Unknown task → `404`
* `POST /tasks` → `201`
* Invalid task body → `400`
* `PUT /tasks/{id}` → `200`
* `DELETE /tasks/{id}` → `204`
* Deleting an unknown task → `404`

## Persistence Test

Persistence was tested by:

1. Running the complete stack with Docker Compose.
2. Creating and reading task data.
3. Stopping the Compose stack with:

```bash
docker compose down
```

4. Starting it again with:

```bash
docker compose up -d
```

5. Calling:

```bash
curl -i http://127.0.0.1:8000/tasks
```

The existing PostgreSQL rows remained available after the restart.

This proves that the Docker volume preserves database data across the container lifecycle.

## Parameterized Queries

Database queries use parameterized placeholders rather than directly inserting user input into SQL statements.

For example, task lookup uses a parameterized query so the task ID is passed separately from the SQL statement.

This prevents user input from being treated as part of the SQL command.

## Database Screenshot

The repository includes evidence of the PostgreSQL database containing the `tasks` table and stored task rows.

The screenshot shows:

* `\dt` confirming the `tasks` table exists.
* `SELECT * FROM tasks;` confirming the stored PostgreSQL rows.

## Project Structure

```text
Week2-Task-API/
├── Dockerfile
├── compose.yaml
├── .env
├── .env.example
├── .gitignore
├── main.py
├── postgres_repository.py
├── requirements.txt
└── README.md
```

`.env` is intentionally excluded from Git.

## Storage Evolution

| Assignment | Storage              |
| ---------- | -------------------- |
| A1         | In-memory            |
| A2         | SQLite               |
| A3         | PostgreSQL in Docker |

The API behaviour remains consistent while the underlying storage implementation changes.

## Author

Pratha Raj