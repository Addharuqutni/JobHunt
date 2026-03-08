from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
import json
import threading
from db import get_connection, init_db, get_all_settings, save_setting

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

DB_PATH = os.path.join(os.path.dirname(__file__), "jobs.db")

# Ensure DB tables exist on startup
init_db()

# Scraper lock state to prevent thread exhaustion DoS
is_scraping = False
scraper_lock = threading.Lock()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/jobs")
def get_jobs(limit: int = 100, source: str = None, search: str = None):
    """Retrieve jobs from the database with optional filtering."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM jobs WHERE 1=1"
    params = []
    
    if source:
        query += " AND LOWER(source) = ?"
        params.append(source.lower())
    
    if search:
        query += " AND (LOWER(title) LIKE ? OR LOWER(company) LIKE ? OR LOWER(location) LIKE ?)"
        search_term = f"%{search.lower()}%"
        params.extend([search_term, search_term, search_term])
    
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"jobs": jobs, "total": len(jobs)}

@app.get("/api/stats")
def get_stats():
    """Retrieve dashboard statistics."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE is_sent = 1")
    sent_jobs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT source) FROM jobs")
    active_sources = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE created_at >= date('now', '-1 day')")
    new_today = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "totalJobs": total_jobs,
        "newToday": new_today,
        "sentToTelegram": sent_jobs,
        "activeSources": active_sources
    }

@app.get("/api/settings")
def get_settings():
    """Retrieve all saved settings."""
    settings = get_all_settings()
    # Parse JSON values back to objects where applicable
    result = {}
    for key, value in settings.items():
        try:
            result[key] = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            result[key] = value
    return result

@app.post("/api/settings")
def update_settings(settings: dict):
    """Save settings to the database."""
    for key, value in settings.items():
        # Serialize complex values as JSON
        if isinstance(value, (dict, list)):
            save_setting(key, json.dumps(value))
        else:
            save_setting(key, str(value))
    return {"status": "saved", "message": "Settings saved successfully."}

def run_scraper_pipeline():
    """Run the scraper pipeline in a separate thread."""
    global is_scraping
    try:
        from main import job_scraper_pipeline
        job_scraper_pipeline()
    except Exception as e:
        print(f"[API] Scraper pipeline error: {e}")
    finally:
        with scraper_lock:
            is_scraping = False

@app.post("/api/scrape")
def trigger_scrape():
    """Trigger scraper pipeline in background."""
    global is_scraping
    
    with scraper_lock:
        if is_scraping:
            raise HTTPException(status_code=429, detail="Scraper pipeline is already running.")
        is_scraping = True
        
    thread = threading.Thread(target=run_scraper_pipeline, daemon=True)
    thread.start()
    return {"status": "started", "message": "Scraper pipeline started in background."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

