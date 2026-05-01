"""
Logging configuration for the trading bot.

Configures Python logging to output to both a log file and the console.
Secrets (API keys) are never logged.
"""

import logging
import os


def setup_logging(log_file="logs/trading.log"):
    """Configure and return the trading bot logger.

    Sets up file and console handlers with appropriate log levels.
    Creates the log directory if it does not exist.
    Prevents duplicate handlers on repeated calls.

    Args:
        log_file: Path to the log file. Defaults to logs/trading.log.

    Returns:
        logging.Logger: Configured logger instance.
    """
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger("trading_bot")

    # Prevent duplicate handlers if setup_logging is called more than once
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # File handler — captures all levels (DEBUG and above)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # Console handler — INFO and above only
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
