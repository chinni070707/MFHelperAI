"""
Database configuration with connection pooling for scalability
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Connection pool settings for production scalability
POOL_SETTINGS = {
    "poolclass": QueuePool,
    "pool_size": 20,           # Base connections always open
    "max_overflow": 40,        # Additional connections under load (total: 60)
    "pool_pre_ping": True,     # Verify connection health before use
    "pool_recycle": 3600,      # Recycle connections every hour
    "pool_timeout": 30,        # Wait up to 30s for available connection
}

# SQLite-specific settings
if "sqlite" in settings.DATABASE_URL:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        # SQLite doesn't support connection pooling well, use NullPool
        poolclass=None,
        echo=False  # SQL echo disabled — use logger for structured query logging
    )
    logger.info("Database: SQLite (development mode, no pooling)")
else:
    # PostgreSQL/MySQL production settings with connection pooling
    engine = create_engine(
        settings.DATABASE_URL,
        **POOL_SETTINGS,
        echo=False  # SQL echo disabled — use logger for structured query logging
    )
    logger.info(f"Database: Production mode with connection pool (size: {POOL_SETTINGS['pool_size']}, max: {POOL_SETTINGS['pool_size'] + POOL_SETTINGS['max_overflow']})")

# Log connection pool events in debug mode
if settings.DEBUG:
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        logger.debug(f"Database connection established: {id(dbapi_conn)}")
    
    @event.listens_for(engine, "checkout")
    def receive_checkout(dbapi_conn, connection_record, connection_proxy):
        logger.debug(f"Connection checked out from pool: {id(dbapi_conn)}")
    
    @event.listens_for(engine, "checkin")
    def receive_checkin(dbapi_conn, connection_record):
        logger.debug(f"Connection returned to pool: {id(dbapi_conn)}")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
