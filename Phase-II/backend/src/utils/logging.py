import logging
from typing import Any
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log"),
    ],
)

logger = logging.getLogger(__name__)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Name of the logger

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

def log_info(message: str, extra: dict[str, Any] | None = None) -> None:
    """
    Log an info message.

    Args:
        message: Message to log
        extra: Additional context to include in the log
    """
    if extra:
        logger.info(message, extra=extra)
    else:
        logger.info(message)

def log_error(message: str, extra: dict[str, Any] | None = None) -> None:
    """
    Log an error message.

    Args:
        message: Message to log
        extra: Additional context to include in the log
    """
    if extra:
        logger.error(message, extra=extra)
    else:
        logger.error(message)

def log_debug(message: str, extra: dict[str, Any] | None = None) -> None:
    """
    Log a debug message.

    Args:
        message: Message to log
        extra: Additional context to include in the log
    """
    if extra:
        logger.debug(message, extra=extra)
    else:
        logger.debug(message)

def log_warning(message: str, extra: dict[str, Any] | None = None) -> None:
    """
    Log a warning message.

    Args:
        message: Message to log
        extra: Additional context to include in the log
    """
    if extra:
        logger.warning(message, extra=extra)
    else:
        logger.warning(message)