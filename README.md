# Task CRUD API

A simple REST API built with Python and FastAPI.

## Project Purpose

This project demonstrates a basic CRUD API with task creation, retrieval, updating, deletion, validation, and error handling.

## Tech Stack

- Python
- FastAPI
- Pydantic
- Uvicorn

## Features

- Create tasks
- Read all tasks
- Read a single task
- Update tasks
- Delete tasks
- Input validation
- 404 error handling
- Health check endpoint
- Interactive Swagger documentation

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API status |
| GET | `/health` | Health check |
| GET | `/tasks` | Get all tasks |
| GET | `/tasks/{task_id}` | Get one task |
| POST | `/tasks` | Create a task |
| PUT | `/tasks/{task_id}` | Update a task |
| DELETE | `/tasks/{task_id}` | Delete a task |

## Installation

Create a virtual environment:

```bash
python -m venv .venv