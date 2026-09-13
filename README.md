# TaskFlow API

A production-style project and task management backend built with Django REST Framework.

This repository is designed as a backend engineering portfolio project and focuses on the parts that matter in real systems: authentication, permissions, relational data modeling, background jobs, caching, containerization, API documentation, and tests.

## Tech Stack

- Python
- Django / Django REST Framework
- PostgreSQL
- Redis
- Celery
- JWT authentication
- Docker / Docker Compose
- drf-spectacular / OpenAPI
- pytest / Django test framework

## Core Features

- JWT login and refresh tokens
- Project ownership and membership
- Role-aware access control
- Task assignment, priority, status, and due dates
- Project-level task summaries cached in Redis
- Background due-date reminder workflow with Celery
- Query filtering by project, status, and priority
- Swagger/OpenAPI documentation
- Health endpoint
- Dockerized API, PostgreSQL, Redis, and Celery worker stack
- Automated API tests covering permissions and core workflows

## Domain Model

### Project

A project has one owner and multiple members. Owners control project-level changes while members can access project data and assigned work.

### Task

Tasks belong to projects and support:

- assignees
- `todo`, `in_progress`, and `done` statuses
- `low`, `medium`, and `high` priorities
- optional due dates
- completion timestamps

## API Overview

### Authentication

```text
POST /api/auth/token/
POST /api/auth/token/refresh/
```

### Projects

```text
GET    /api/projects/
POST   /api/projects/
GET    /api/projects/{id}/
PUT    /api/projects/{id}/
PATCH  /api/projects/{id}/
DELETE /api/projects/{id}/
GET    /api/projects/{id}/summary/
```

### Tasks

```text
GET    /api/tasks/
POST   /api/tasks/
GET    /api/tasks/{id}/
PUT    /api/tasks/{id}/
PATCH  /api/tasks/{id}/
DELETE /api/tasks/{id}/
POST   /api/tasks/{id}/complete/
```

Filtering examples:

```text
GET /api/tasks/?project=1
GET /api/tasks/?status=in_progress
GET /api/tasks/?priority=high
```

### Documentation

```text
GET /api/schema/
GET /api/docs/
GET /health/
```

## Architecture Notes

### PostgreSQL

Projects, users, memberships, and tasks are modeled relationally. Task queries use indexes on project/status and assignee/due date combinations to support common access patterns.

### Redis

Redis is used for two separate backend concerns:

1. caching computed project summaries
2. acting as the Celery broker/result backend

This keeps request-time work lightweight while allowing background processing to scale independently.

### Celery

The worker layer includes a due-task reminder workflow that finds incomplete tasks due within the next 24 hours and sends notifications asynchronously.

### Permissions

The API scopes project and task querysets to the authenticated user. Project ownership is enforced for write-sensitive operations, while members can access project work they belong to.

## Local Setup

Clone the repository and create an environment file:

```bash
cp .env.example .env
```

Update the values in `.env`, then start the stack:

```bash
docker compose up --build
```

Run migrations:

```bash
docker compose exec api python manage.py makemigrations
docker compose exec api python manage.py migrate
```

Create an admin user if needed:

```bash
docker compose exec api python manage.py createsuperuser
```

The API will be available at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/api/docs/
```

## Running Tests

```bash
python manage.py test
```

or inside Docker:

```bash
docker compose exec api python manage.py test
```

## Security Notes

- secrets and database credentials are loaded from environment variables
- `.env` files are excluded from version control
- the repository contains no production credentials
- JWT is used for API authentication

## Why This Project Exists

Most of my recent production backend work lives in private company repositories. TaskFlow is a public demonstration of the same engineering patterns I work with professionally: Python APIs, PostgreSQL data modeling, Redis/Celery asynchronous workflows, permissions, caching, Docker, testing, and production-minded architecture.

## Author

**Chiagozie Stanley Nwobodo**  
Python Backend Engineer

- GitHub: https://github.com/AG-042
- LinkedIn: https://www.linkedin.com/in/chiagozie-stanley-nwobodo
