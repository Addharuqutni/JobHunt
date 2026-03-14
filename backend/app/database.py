from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# If using SQLite, we need connect_args={"check_same_thread": False}
connect_args = {"check_same_thread": False} if settings.DB_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DB_URL, 
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
