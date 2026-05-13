# JobSentinel — Job Scraping & Notification Platform

A full-stack job scraping platform with automated Telegram notifications, built with **Clean Architecture** principles.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + TypeScript + Vite |
| Backend | Python + FastAPI + SQLAlchemy |
| Database | PostgreSQL |
| Queue | Redis + Celery (optional) |
| Scrapers | Jobstreet, Glints, Kalibrr, Dealls |

## Architecture

### Backend — Clean Architecture

```
backend/app/
├── domain/          # Pure entities, interfaces, value objects (ZERO deps)
├── use_cases/       # Application business rules
├── adapters/        # Repository & gateway implementations
├── api/             # HTTP routes, schemas, app factory
├── core/            # Config, DB, security, DI container
└── scrapers/        # External scraper adapters
```

### Frontend — Feature-Based

```
src/
├── features/        # Domain features (dashboard, jobs, scraper, settings)
│   └── <feature>/
│       ├── components/
│       ├── hooks/
│       ├── services/
│       └── types.ts
├── shared/          # Reusable hooks, utils, types, constants
├── config/          # API configuration
└── layouts/         # Page layouts
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### Backend Setup

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env     # Edit with your DB credentials

# Start the API server
uvicorn app.api.app:app --reload --port 8000
```

### Frontend Setup

```bash
npm install
npm run dev
```

### Run Tests

```bash
cd backend
.\venv\Scripts\pytest.exe tests/unit/ -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/jobs` | List jobs with filtering |
| GET | `/api/stats` | Dashboard statistics |
| GET | `/api/settings` | Retrieve settings |
| POST | `/api/settings` | Update settings |
| POST | `/api/scrape` | Trigger scraper pipeline |
| WS | `/api/ws/scrape-status` | Real-time scraper progress |
| GET | `/health` | Health check |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_KEY` | `dev-secret-key-123` | API authentication key |
| `POSTGRES_USER` | `jobsentinel` | Database user |
| `POSTGRES_PASSWORD` | `jobsentinel123` | Database password |
| `POSTGRES_HOST` | `localhost` | Database host |
| `POSTGRES_PORT` | `5432` | Database port |
| `POSTGRES_DB` | `jobsentinel` | Database name |
| `USE_REDIS` | `false` | Enable Redis/Celery mode |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |

## Docker

```bash
docker-compose up -d
```

## License

Private project.
