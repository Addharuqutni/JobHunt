from fastapi import FastAPI, Header, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
import json
import redis
import threading
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.database import get_db, engine
from app.models import Job, Setting, Base
from db import get_all_settings, save_setting

API_KEY = os.environ.get("API_KEY", "dev-secret-key-123")

async def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return x_api_key

# Apply authentication to all endpoints globally
app = FastAPI(dependencies=[Depends(verify_api_key)])

# Restrict CORS to exact frontend origins to prevent CSRF
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure DB tables exist on startup (Alembic handles this fully later)
Base.metadata.create_all(bind=engine)

# Redis configuration with explicit local-only toggle
from app.config import settings
USE_REDIS = os.environ.get("USE_REDIS", "false").lower() == "true"

IS_REDIS_AVAILABLE = False
redis_client = None

if USE_REDIS:
    try:
        redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        redis_client.ping()
        IS_REDIS_AVAILABLE = True
        print(f"[Redis] Connected to {settings.REDIS_URL}")
    except Exception as e:
        print(f"[Redis] Failed to connect: {e}. Falling back to LOCAL mode.")
else:
    print("[System] Redis is DISABLED. Using local execution mode.")

# Local lock fallback
scraper_lock = threading.Lock()
is_scraping_local = False # Track local state if redis is down

@app.get("/api/jobs")
def get_jobs(limit: int = 100, source: str = None, search: str = None, db: Session = Depends(get_db)):
    """Retrieve jobs from the database with optional filtering."""
    query = db.query(Job)
    
    if source:
        query = query.filter(func.lower(Job.source) == source.lower())
    
    if search:
        search_term = f"%{search.lower()}%"
        query = query.filter(
            or_(
                func.lower(Job.title).like(search_term),
                func.lower(Job.company).like(search_term),
                func.lower(Job.location).like(search_term)
            )
        )
    
    jobs = query.order_by(Job.created_at.desc()).limit(limit).all()
    
    # Format to match existing React frontend expectations
    job_dicts = []
    for j in jobs:
        job_dicts.append({
            "id": j.id,
            "job_hash": j.job_hash,
            "title": j.title,
            "company": j.company,
            "location": j.location,
            "url": j.url,
            "source": j.source,
            "is_sent": 1 if j.is_sent else 0,
            "created_at": j.created_at.isoformat() if j.created_at else None
        })
        
    return {"jobs": job_dicts, "total": len(jobs)}

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """Retrieve dashboard statistics."""
    total_jobs = db.query(func.count(Job.id)).scalar()
    sent_jobs = db.query(func.count(Job.id)).filter(Job.is_sent == True).scalar()
    
    # Active sources
    active_sources_count = db.query(func.count(func.distinct(Job.source))).scalar()
    
    # New today (SQLite uses text dates natively, SA does its best depending on DB dialect.
    # For robust cross-DB compatibility, a timezone aware comparison is best, but we'll use a direct filter)
    from datetime import datetime, timedelta
    yesterday = datetime.now() - timedelta(days=1)
    new_today = db.query(func.count(Job.id)).filter(Job.created_at >= yesterday).scalar()
    
    return {
        "totalJobs": total_jobs,
        "newToday": new_today,
        "sentToTelegram": sent_jobs,
        "activeSources": active_sources_count
    }

@app.get("/api/settings")
def get_settings(db: Session = Depends(get_db)):
    """Retrieve all saved settings."""
    settings = get_all_settings(db)
    # Parse JSON values back to objects where applicable
    result = {}
    for key, value in settings.items():
        try:
            result[key] = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            result[key] = value
    return result

@app.post("/api/settings")
def update_settings(settings: dict, db: Session = Depends(get_db)):
    """Save settings to the database."""
    for key, value in settings.items():
        # Serialize complex values as JSON
        if isinstance(value, (dict, list)):
            save_setting(key, json.dumps(value), db)
        else:
            save_setting(key, str(value), db)
    return {"status": "saved", "message": "Settings saved successfully."}

@app.post("/api/scrape")
def trigger_scrape():
    """Trigger scraper pipeline. Uses Redis/Celery if enabled, otherwise local threading."""
    global is_scraping_local
    
    if USE_REDIS and IS_REDIS_AVAILABLE:
        try:
            # Attempt to acquire a distributed lock in Redis for max 1 hour
            acquired = redis_client.set("scraper_lock", "1", nx=True, ex=3600)
            if not acquired:
                raise HTTPException(status_code=429, detail="Scraper is already running (Redis Lock).")
                
            from app.worker import run_job_scraper
            run_job_scraper.delay()  # Dispatch to Celery worker Queue
            return {"status": "started", "message": "Scraper task dispatched to Celery worker."}
        except Exception as e:
            print(f"[Redis] Error dispatching task: {e}. Falling back to local.")

    # LOCAL MODE (Standard threading)
    with scraper_lock:
        if is_scraping_local:
            raise HTTPException(status_code=429, detail="Scraper is already running locally.")
        is_scraping_local = True

    def run_local_task():
        global is_scraping_local
        try:
            # In local mode, we run the pipeline in the same process but in a background thread
            from main import job_scraper_pipeline
            job_scraper_pipeline()
        finally:
            with scraper_lock:
                is_scraping_local = False

    thread = threading.Thread(target=run_local_task, daemon=True)
    thread.start()
    return {"status": "started", "message": "Scraper started in local background thread (Redis/Celery disabled)."}

@app.websocket("/api/ws/scrape-status")
async def websocket_scrape_status(websocket: WebSocket, api_key: str = None):
    """WebSocket endpoint to stream real-time scraping progress."""
    if api_key != API_KEY:
        await websocket.close(code=1008, reason="Unauthorized")
        return

    await websocket.accept()
    
    if not IS_REDIS_AVAILABLE:
        # If no redis, we can't do pubsub easily. We'll just stay open but send nothing
        # or send a warning.
        await websocket.send_json({"message": "Real-time updates disabled (Redis unavailable)", "progress": 0})
        # Keep connection alive so it doesn't spam reconnection
        try:
            while True:
                await asyncio.sleep(10)
        except WebSocketDisconnect:
            return

    pubsub = redis_client.pubsub()
    pubsub.subscribe("scrape_progress")
    
    try:
        while True:
            # Poll for messages
            message = pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                await websocket.send_text(message['data'])
                
            await asyncio.sleep(0.5)
            
    except WebSocketDisconnect:
        pass
    finally:
        pubsub.unsubscribe("scrape_progress")
        pubsub.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

