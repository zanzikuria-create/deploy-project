# Deploy Project — FastAPI + SQLModel + PostgreSQL

A FastAPI REST API with SQLModel-backed CRUD, file uploads, mocked external API integration, a full pytest test suite (92% coverage), Docker packaging, and automated CI/CD deployment to Render.

**Live API:** https://deploy-project-z47q.onrender.com
**Interactive docs:** https://deploy-project-z47q.onrender.com/docs

## Features

- Product and User CRUD backed by PostgreSQL (SQLite locally)
- File upload endpoint with content-type validation
- Weather endpoint demonstrating external API integration (mocked in tests)
- Environment-based configuration via `pydantic-settings`
- CORS middleware
- Structured logging
- Database-aware health check endpoint
- Dockerized for consistent local/production parity
- GitHub Actions CI/CD: tests run on every push, deploy only on success

## Tech Stack

- **FastAPI** — web framework
- **SQLModel** (SQLAlchemy + Pydantic) — ORM and validation
- **PostgreSQL** — production database (via `psycopg2-binary`)
- **SQLite** — local development and test database
- **pytest** + **pytest-cov** — testing
- **Docker** — containerization
- **Render** — hosting (web service + managed PostgreSQL)
- **GitHub Actions** — CI/CD

## Environment Variables

Create a `.env` file in the project root (it's git-ignored — never commit it):

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | Database connection string | `sqlite:///app.db` |
| `SECRET_KEY` | Secret key for future auth features | dev placeholder |
| `ALGORITHM` | JWT algorithm (reserved for future auth) | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry (reserved for future auth) | `30` |
| `WEATHER_API_KEY` | API key for the weather endpoint | `demo_key` |
| `UPLOAD_DIR` | Directory for uploaded files | `uploads` |

In production (Render), `DATABASE_URL` is set to the PostgreSQL **Internal Database URL** provided by Render's managed Postgres instance.

## Local Development

```bash
# Install dependencies
uv sync

# Run the dev server
uv run uvicorn app.main:app --reload

# Visit the interactive docs
# http://127.0.0.1:8000/docs
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=term-missing

# Run a specific test
uv run pytest test_app.py::test_create_product
```

Current coverage: **92%** (target: 80%+).

## Running with Docker

```bash
docker build -t my-api-project .
docker run -p 8000:8000 my-api-project
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | Root/welcome message |
| GET | `/health` | Health check (verifies DB connectivity) |
| POST | `/products` | Create a product |
| GET | `/products/{id}` | Get a product |
| DELETE | `/products/{id}` | Delete a product |
| POST | `/upload` | Upload a file (image types only) |
| GET | `/weather/{city}` | Get mocked/external weather data |
| POST | `/users` | Create a user (unique email enforced) |
| GET | `/users/{id}` | Get a user |
| PUT | `/users/{id}` | Update a user |
| DELETE | `/users/{id}` | Delete a user |

## Usage Examples

**Create a product:**
```bash
curl -X POST https://deploy-project-z47q.onrender.com/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "price": 999.99, "stock": 10}'
```

**Create a user:**
```bash
curl -X POST https://deploy-project-z47q.onrender.com/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com"}'
```

**Upload a file:**
```bash
curl -X POST https://deploy-project-z47q.onrender.com/upload \
  -F "file=@photo.jpg;type=image/jpeg"
```

## Deployment

Deployed on [Render](https://render.com) as a Dockerized web service with a managed PostgreSQL database.

- **CI/CD:** GitHub Actions (`.github/workflows/deploy.yml`) runs the full test suite on every push to `main`. Deployment to Render is triggered automatically only if all tests pass.
- **Manual deploy:** Render also auto-deploys on push via its native GitHub integration, independent of the Actions workflow.

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py          # Routes and app setup
│   ├── database.py      # Engine and session management
│   └── settings.py      # Environment-based configuration
├── .github/workflows/
│   └── deploy.yml       # CI/CD pipeline
├── test_app.py           # Test suite
├── conftest.py           # Test database fixtures
├── Dockerfile
├── .dockerignore
├── .gitignore
├── pyproject.toml
└── uv.lock
```