import sqlite3
import os
import hashlib
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "jobs.db")

def get_connection():
    """Get a database connection with row_factory set."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create the jobs table if it doesn't exist."""
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_hash TEXT UNIQUE,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT,
                url TEXT NOT NULL,
                source TEXT NOT NULL,
                is_sent BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def generate_job_hash(title, company, url):
    """Generate a unique hash for a job based on title, company, and url."""
    hash_str = f"{title}_{company}_{url}".lower()
    return hashlib.md5(hash_str.encode()).hexdigest()

def save_job(title, company, location, url, source):
    """Save a new job to the database. Returns True if inserted, False if duplicate.
    Uses INSERT OR IGNORE to atomically handle duplicates without race conditions."""
    job_hash = generate_job_hash(title, company, url)
    with get_connection() as conn:
        cursor = conn.execute('''
            INSERT OR IGNORE INTO jobs (job_hash, title, company, location, url, source, is_sent, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?)
        ''', (job_hash, title, company, location, url, source, datetime.now()))
        conn.commit()
        return cursor.rowcount > 0

def get_unsent_jobs():
    """Retrieve all jobs that haven't been sent to Telegram yet."""
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM jobs WHERE is_sent = 0 ORDER BY created_at ASC")
        return [dict(row) for row in cursor.fetchall()]

def mark_jobs_as_sent(job_ids):
    """Update is_sent status for specific jobs."""
    if not job_ids:
        return
    with get_connection() as conn:
        placeholders = ','.join('?' for _ in job_ids)
        conn.execute(f"UPDATE jobs SET is_sent = 1 WHERE id IN ({placeholders})", job_ids)
        conn.commit()

def get_setting(key, default=None):
    """Get a setting value from the database."""
    with get_connection() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row[0] if row else default

def save_setting(key, value):
    """Save or update a setting in the database."""
    with get_connection() as conn:
        conn.execute('''
            INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
        ''', (key, value, datetime.now()))
        conn.commit()

def get_all_settings():
    """Get all settings as a dictionary."""
    with get_connection() as conn:
        rows = conn.execute("SELECT key, value FROM settings").fetchall()
        return {row[0]: row[1] for row in rows}

if __name__ == "__main__":
    init_db()
    print("Database initialized at", DB_PATH)

