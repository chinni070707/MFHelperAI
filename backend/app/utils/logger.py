"""
Centralized Logging Configuration
Provides structured logging with proper formatting and log levels
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',  # Cyan
        'INFO': '\033[32m',  # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',  # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'  # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logging(log_level=logging.INFO, enable_file_logging=True):
    """
    Setup application-wide logging
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_file_logging: Whether to enable file logging
    """
    
    log_file = None  # Initialize to None for type checking
    
    # Create logs directory if it doesn't exist
    if enable_file_logging:
        log_dir = Path(__file__).parent.parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"mfhelper_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console Handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = ColoredFormatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File Handler with rotation (if enabled)
    if enable_file_logging and log_file is not None:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Set logging levels for third-party libraries
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('fastapi').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info(f"MFHelper Logging initialized - Level: {logging.getLevelName(log_level)}")
    logger.info(f"File logging: {'Enabled' if enable_file_logging else 'Disabled'}")
    if enable_file_logging:
        logger.info(f"Log file: {log_file}")
    logger.info("=" * 80)


def log_request(method: str, path: str, status_code: int, duration_ms: float):
    """Log HTTP request with timing"""
    logger = logging.getLogger('mfhelper.requests')
    
    if status_code < 400:
        level = logging.INFO
    elif status_code < 500:
        level = logging.WARNING
    else:
        level = logging.ERROR
    
    logger.log(
        level,
        f"{method} {path} - {status_code} - {duration_ms:.2f}ms"
    )


def log_user_action(user_id: str, action: str, details: dict | None = None):
    """Log user actions for audit trail"""
    logger = logging.getLogger('mfhelper.audit')
    logger.info(
        f"User: {user_id} | Action: {action}" + 
        (f" | Details: {details}" if details else "")
    )


def log_db_query(query: str, duration_ms: float, rows_affected: int = 0):
    """Log database queries with timing"""
    logger = logging.getLogger('mfhelper.database')
    logger.debug(
        f"Query executed in {duration_ms:.2f}ms | Rows: {rows_affected} | SQL: {query[:100]}"
    )


# Performance tracking decorator
def log_execution_time(func):
    """Decorator to log function execution time"""
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            logger.debug(f"{func.__name__} executed in {duration:.2f}ms")
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"{func.__name__} failed after {duration:.2f}ms: {str(e)}")
            raise
    
    return wrapper


# Async version
def log_async_execution_time(func):
    """Decorator to log async function execution time"""
    import functools
    import time
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            logger.debug(f"{func.__name__} executed in {duration:.2f}ms")
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"{func.__name__} failed after {duration:.2f}ms: {str(e)}")
            raise
    
    return wrapper


# Exception logging helper
def log_exception(logger, exc: Exception, context: str = ""):
    """
    Log exception with full context
    
    Args:
        logger: Logger instance
        exc: Exception object
        context: Additional context string
    """
    logger.error(
        f"Exception occurred{f' in {context}' if context else ''}: "
        f"{type(exc).__name__}: {str(exc)}",
        exc_info=True
    )


if __name__ == "__main__":
    # Test the logging setup
    setup_logging(log_level=logging.DEBUG)
    
    test_logger = logging.getLogger(__name__)
    test_logger.debug("This is a DEBUG message")
    test_logger.info("This is an INFO message")
    test_logger.warning("This is a WARNING message")
    test_logger.error("This is an ERROR message")
    test_logger.critical("This is a CRITICAL message")
    
    # Test performance decorator
    @log_execution_time
    def test_function():
        import time
        time.sleep(0.1)
        return "Done"
    
    test_function()
