"""SQLite database connection and session management."""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# SQLite database URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{settings.DB_PATH}"

# Create engine with SQLite-specific settings
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite
    echo=settings.DEBUG  # Log SQL queries in debug mode
)

# Enable foreign keys for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    from . import models  # Import models to register them
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database initialized at {settings.DB_PATH}")
