from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# Tạo engine kết nối đến SQLite database
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Để cho phép multi-thread access
)

# Tạo session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Session:
    """
    Dependency để lấy database session trong FastAPI endpoints
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()