"""
Logging Configuration - EduAutismo IA

Provides structured logging with support for:
- Console and file output
- JSON formatting for production
- Request ID tracking
- Log level filtering
- Rotating file handlers
"""

import json
import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add custom fields
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id

        if hasattr(record, "extra"):
            log_data["extra"] = record.extra

        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""

    # Color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        log_color = self.COLORS.get(record.levelname, self.RESET)

        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")

        # Build log message
        parts = [
            f"{log_color}[{record.levelname}]{self.RESET}",
            f"{timestamp}",
            f"{record.name}",
            f"{record.getMessage()}",
        ]

        # Add request ID if present
        if hasattr(record, "request_id"):
            parts.insert(2, f"[{record.request_id}]")

        log_message = " - ".join(parts)

        # Add exception info if present
        if record.exc_info:
            log_message += f"\n{self.formatException(record.exc_info)}"

        return log_message


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    json_logs: bool = False,
) -> None:
    """
    Setup application logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        json_logs: Use JSON formatting (default: False, True in production)
    """
    # Get log level from settings or parameter
    level_name = log_level or settings.LOG_LEVEL
    level = getattr(logging, level_name.upper(), logging.INFO)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Use JSON formatter in production, colored formatter in development
    if json_logs or settings.ENVIRONMENT == "production":
        console_formatter = JSONFormatter()
    else:
        console_formatter = ColoredFormatter()

    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler (if log file specified or in production)
    if log_file or settings.ENVIRONMENT == "production":
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Use provided log file or default
        log_path = log_file or log_dir / f"{settings.APP_NAME.lower().replace(' ', '_')}.log"

        # Rotating file handler (10MB max, keep 5 backups)
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(level)

        # Always use JSON format for file logs
        file_formatter = JSONFormatter()
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Set third-party loggers to WARNING
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    # Log initial message
    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configured: level={level_name}, env={settings.ENVIRONMENT}, "
        f"json_logs={json_logs or settings.ENVIRONMENT == 'production'}"
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class RequestIDFilter(logging.Filter):
    """Filter to add request ID to log records."""

    def __init__(self, request_id: str):
        super().__init__()
        self.request_id = request_id

    def filter(self, record: logging.LogRecord) -> bool:
        """Add request ID to record."""
        record.request_id = self.request_id
        return True


def add_request_context(logger: logging.Logger, request_id: str) -> logging.Logger:
    """
    Add request context to logger.

    Args:
        logger: Logger instance
        request_id: Request ID to track

    Returns:
        Logger with request context
    """
    logger.addFilter(RequestIDFilter(request_id))
    return logger


# Convenience functions for common logging patterns
def log_request(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    request_id: Optional[str] = None,
) -> None:
    """
    Log HTTP request.

    Args:
        logger: Logger instance
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
        request_id: Request ID (optional)
    """
    level = logging.INFO if status_code < 400 else logging.WARNING

    extra_data = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
    }

    if request_id:
        extra_data["request_id"] = request_id

    logger.log(
        level,
        f"{method} {path} {status_code} - {duration_ms:.2f}ms",
        extra={"extra": extra_data},
    )


def log_exception(
    logger: logging.Logger,
    exception: Exception,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log exception with context.

    Args:
        logger: Logger instance
        exception: Exception to log
        context: Additional context data
    """
    extra_data = {
        "exception_type": type(exception).__name__,
        "exception_message": str(exception),
    }

    if context:
        extra_data.update(context)

    logger.error(
        f"Exception occurred: {type(exception).__name__}: {exception}",
        exc_info=True,
        extra={"extra": extra_data},
    )


def log_database_query(
    logger: logging.Logger,
    query: str,
    duration_ms: float,
    rows_affected: Optional[int] = None,
) -> None:
    """
    Log database query.

    Args:
        logger: Logger instance
        query: SQL query
        duration_ms: Query duration in milliseconds
        rows_affected: Number of rows affected (optional)
    """
    extra_data = {
        "query": query[:200],  # Truncate long queries
        "duration_ms": round(duration_ms, 2),
    }

    if rows_affected is not None:
        extra_data["rows_affected"] = rows_affected

    # Warn on slow queries (>1s)
    level = logging.WARNING if duration_ms > 1000 else logging.DEBUG

    logger.log(
        level,
        f"DB Query: {duration_ms:.2f}ms",
        extra={"extra": extra_data},
    )


def log_openai_request(
    logger: logging.Logger,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    duration_ms: float,
    request_id: Optional[str] = None,
) -> None:
    """
    Log OpenAI API request.

    Args:
        logger: Logger instance
        model: Model used
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
        duration_ms: Request duration in milliseconds
        request_id: Request ID (optional)
    """
    extra_data = {
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "duration_ms": round(duration_ms, 2),
    }

    if request_id:
        extra_data["request_id"] = request_id

    logger.info(
        f"OpenAI Request: {model} - {prompt_tokens + completion_tokens} tokens - {duration_ms:.2f}ms",
        extra={"extra": extra_data},
    )


# Initialize logging on module import
if not logging.getLogger().handlers:
    setup_logging()
