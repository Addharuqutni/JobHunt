import hashlib
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from app.database import SessionLocal, engine
from app.models import Job, Setting, Base

def init_db():
    # Will be handled by Alembic in the future, but leaving for backwards compatibility during transition
    Base.metadata.create_all(bind=engine)

def generate_job_hash(title, company, url):
    """Generate a unique hash for a job based on title, company, and url."""
    hash_str = f"{title}_{company}_{url}".lower()
    return hashlib.md5(hash_str.encode()).hexdigest()

def save_job(title, company, location, url, source, posted_at=None, db: Session = None):
    """Save a new job to the database."""
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        job_hash = generate_job_hash(title, company, url)
        
        # SQLite specific UPSERT logic. Once we move to Postgres fully, this needs PG dialect.
        # But wait, we want ignore on duplicate, not update.
        existing_job = db.query(Job).filter(Job.job_hash == job_hash).first()
        if existing_job:
            return False

        new_job = Job(
            job_hash=job_hash,
            title=title,
            company=company,
            location=location,
            url=url,
            source=source,
            posted_at=posted_at,
            is_sent=False,
            created_at=datetime.now()
        )
        try:
            db.add(new_job)
            db.commit()
            return True
        except IntegrityError:
            db.rollback()
            return False
            
    finally:
        if close_db:
            db.close()

def get_unsent_jobs(db: Session = None):
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
        
    try:
        jobs = db.query(Job).filter(Job.is_sent == False).order_by(Job.created_at.asc()).all()
        # Convert to dict to match previous interface
        return [{"id": j.id, "job_hash": j.job_hash, "title": j.title, "company": j.company, 
                 "location": j.location, "url": j.url, "source": j.source, 
                 "posted_at": j.posted_at, "is_sent": j.is_sent, "created_at": j.created_at} for j in jobs]
    finally:
        if close_db:
            db.close()

def mark_jobs_as_sent(job_ids, db: Session = None):
    if not job_ids:
        return
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
        
    try:
        db.query(Job).filter(Job.id.in_(job_ids)).update({"is_sent": True})
        db.commit()
    finally:
        if close_db:
            db.close()

def get_setting(key, default=None, db: Session = None):
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
        
    try:
        setting = db.query(Setting).filter(Setting.key == key).first()
        return setting.value if setting else default
    finally:
        if close_db:
            db.close()

def save_setting(key, value, db: Session = None):
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
        
    try:
        setting = db.query(Setting).filter(Setting.key == key).first()
        if setting:
            setting.value = str(value)
            setting.updated_at = datetime.now()
        else:
            db.add(Setting(key=key, value=str(value), updated_at=datetime.now()))
        db.commit()
    finally:
        if close_db:
            db.close()

def get_all_settings(db: Session = None):
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
        
    try:
        settings = db.query(Setting).all()
        return {s.key: s.value for s in settings}
    finally:
        if close_db:
            db.close()

if __name__ == "__main__":
    init_db()
    print("Database models initialized via SQLAlchemy.")

