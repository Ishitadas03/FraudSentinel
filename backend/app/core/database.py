"""Database engine setup, connection pooling, and session management."""

from __future__ import annotations

from contextlib import contextmanager
import logging
import os
from pathlib import Path
import tempfile
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from app.core.config import settings

logger = logging.getLogger("fraudsentinel.database")


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy ORM models."""
    pass


def _resolve_sqlite_path() -> Path:
    """Return a writable SQLite path, defaulting to temp directory in serverless environments."""
    is_serverless = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
    if is_serverless:
        return Path(tempfile.gettempdir()) / "fraudsentinel.db"
    return Path(__file__).resolve().parent.parent.parent / "fraudsentinel.db"


def init_engine():
    """Initializes SQLAlchemy database engine with automatic fallback for local development and serverless."""
    db_url = settings.DATABASE_URL
    is_serverless = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))

    # In serverless environments, if using SQLite or localhost DB without remote Postgres, redirect to /tmp
    if is_serverless and (db_url.startswith("sqlite") or "localhost" in db_url or "127.0.0.1" in db_url):
        sqlite_path = _resolve_sqlite_path()
        sqlite_url = f"sqlite:///{sqlite_path}"
        sqlite_engine = create_engine(
            sqlite_url,
            connect_args={"check_same_thread": False},
            echo=settings.DB_ECHO,
        )

        @event.listens_for(sqlite_engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        logger.info("Serverless runtime detected: Initialized SQLite at %s", sqlite_url)
        return sqlite_engine

    if db_url.startswith("postgresql://") or db_url.startswith("postgres://"):
        try:
            pg_engine = create_engine(
                db_url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                echo=settings.DB_ECHO,
                connect_args={"connect_timeout": 3},
            )
            with pg_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to PostgreSQL at %s", db_url)
            return pg_engine
        except Exception as e:
            logger.warning(
                "PostgreSQL not accessible at %s (%s). Falling back to local SQLite database.",
                db_url,
                e,
            )
            sqlite_path = _resolve_sqlite_path()
            sqlite_url = f"sqlite:///{sqlite_path}"
            sqlite_engine = create_engine(
                sqlite_url,
                connect_args={"check_same_thread": False},
                echo=settings.DB_ECHO,
            )

            @event.listens_for(sqlite_engine, "connect")
            def _set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

            return sqlite_engine
    else:
        connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
        return create_engine(db_url, connect_args=connect_args, echo=settings.DB_ECHO)


# Global database engine
engine = init_engine()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

_db_initialized = False


def ensure_db_initialized():
    """Ensure database schema and baseline seed roles/users exist."""
    global _db_initialized
    if _db_initialized:
        return
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            from scripts.seed import seed_roles, seed_default_users
            roles = seed_roles(db)
            seed_default_users(db, roles)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.warning("Startup seeding check notice: %s", e)
        finally:
            db.close()
        _db_initialized = True
    except Exception as err:
        logger.warning("Database startup init notice: %s", err)


# FastAPI database session dependency
def get_db() -> Generator[Session, None, None]:
    """Yield a database session for FastAPI dependency injection."""
    ensure_db_initialized()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database sessions in scripts and non-FastAPI code."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
