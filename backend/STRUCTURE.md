# Backend Architecture — Clean Architecture

## Overview

This backend follows **Clean Architecture** principles with clear separation of concerns.
Dependencies flow inward: API → Use Cases → Domain ← Adapters.

## Directory Structure

```
backend/
├── app/
│   ├── api/                        # HTTP Transport Layer
│   │   ├── app.py                  # FastAPI app factory
│   │   ├── router.py               # Main router aggregator
│   │   ├── routes/                 # Feature-based route modules
│   │   │   ├── jobs.py             # GET /api/jobs
│   │   │   ├── stats.py            # GET /api/stats
│   │   │   ├── settings.py         # GET/POST /api/settings
│   │   │   ├── scraper.py          # POST /api/scrape
│   │   │   └── websocket.py        # WS /api/ws/scrape-status
│   │   └── schemas/                # Pydantic request/response DTOs
│   │       ├── job_schemas.py
│   │       ├── setting_schemas.py
│   │       └── common.py
│   │
│   ├── use_cases/                  # Application Business Rules
│   │   ├── jobs/
│   │   │   ├── get_jobs.py         # GetJobsUseCase
│   │   │   ├── get_stats.py        # GetStatsUseCase
│   │   │   └── save_job.py         # SaveJobUseCase
│   │   └── settings/
│   │       ├── get_settings.py     # GetSettingsUseCase
│   │       └── update_settings.py  # UpdateSettingsUseCase
│   │
│   ├── domain/                     # Core Business Logic (NO framework deps)
│   │   ├── entities/
│   │   │   ├── job.py              # Job entity with validation & enrichment
│   │   │   └── setting.py          # Setting entity
│   │   ├── interfaces/             # Ports (abstract contracts)
│   │   │   ├── job_repository.py   # IJobRepository
│   │   │   ├── setting_repository.py # ISettingRepository
│   │   │   └── notification_gateway.py # INotificationGateway
│   │   └── value_objects/
│   │       └── job_hash.py         # JobHash (immutable dedup hash)
│   │
│   ├── adapters/                   # Interface Implementations
│   │   ├── repositories/
│   │   │   ├── sqlalchemy_job_repository.py
│   │   │   └── sqlalchemy_setting_repository.py
│   │   ├── gateways/
│   │   │   ├── telegram_gateway.py
│   │   │   └── redis_pubsub_gateway.py
│   │   └── orm/
│   │       ├── models.py           # SQLAlchemy table definitions
│   │       └── mappers.py          # Entity ↔ ORM mapping
│   │
│   ├── core/                       # Infrastructure & Cross-Cutting
│   │   ├── config.py               # Environment configuration
│   │   ├── database.py             # DB engine & session factory
│   │   ├── dependencies.py         # FastAPI DI container
│   │   ├── security.py             # API key verification
│   │   └── exceptions.py           # Custom exception hierarchy
│   │
│   ├── scrapers/                   # External Scraper Adapters
│   │   ├── base_scraper.py
│   │   ├── jobstreet.py
│   │   ├── glints_v2.py
│   │   ├── kalibrr_v2.py
│   │   └── dealls_v2.py
│   │
│   ├── services/                   # Legacy services (backward compat)
│   │   ├── db.py
│   │   ├── telegram.py
│   │   └── worker.py
│   │
│   └── models/                     # Legacy models (backward compat)
│       └── job.py
│
├── main.py                         # Scraper pipeline entry point
├── alembic/                        # Database migrations
├── tests/                          # Test suite
├── requirements.txt
└── .env
```

## Dependency Flow

```
┌─────────────────────────────────────────┐
│           API Layer (routes)            │
│  Thin controllers, Pydantic schemas     │
└──────────────────┬──────────────────────┘
                   │ depends on
                   ▼
┌─────────────────────────────────────────┐
│         Use Cases (business rules)      │
│  Single-responsibility orchestrators    │
└──────────────────┬──────────────────────┘
                   │ depends on
                   ▼
┌─────────────────────────────────────────┐
│         Domain (entities, ports)        │
│  Pure Python, ZERO external deps        │
└─────────────────────────────────────────┘
                   ▲
                   │ implements
┌─────────────────────────────────────────┐
│       Adapters (repositories, gateways) │
│  SQLAlchemy, Redis, Telegram API        │
└─────────────────────────────────────────┘
```

## Key Patterns

| Pattern | Implementation |
|---------|---------------|
| Repository | `IJobRepository` → `SQLAlchemyJobRepository` |
| Gateway | `INotificationGateway` → `TelegramGateway` |
| Use Case | Single class per operation (e.g., `SaveJobUseCase`) |
| Value Object | `JobHash` — immutable, identity by value |
| Entity | `Job` — has identity, mutable state, business rules |
| DI Container | `core/dependencies.py` via FastAPI `Depends` |
| App Factory | `api/app.py` → `create_app()` |

## Running

```bash
# New architecture entry point
uvicorn app.api.app:app --reload --host 0.0.0.0 --port 8000

# Legacy entry point (still works)
uvicorn app.api.routes:app --reload --host 0.0.0.0 --port 8000
```
