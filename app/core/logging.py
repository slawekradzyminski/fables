import logging
import sys
from pathlib import Path
from typing import Any, Dict

from app.core.config import get_settings

settings = get_settings()

def setup_logging() -> None:
    """Configure logging with a standard format and file/console handlers."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    root_logger.addHandler(file_handler)

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(name)

def log_request_response(logger: logging.Logger, request: Dict[str, Any], response: Dict[str, Any]) -> None:
    """Log request and response data in a structured format."""
    logger.info(
        "API request/response",
        extra={
            "request": request,
            "response": response,
        }
    ) 