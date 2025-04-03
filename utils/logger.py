import logging
import os
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


def setup_logger(
    logger_name: str = "app",
    log_level: int = logging.INFO,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_file: str = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
    console_output: bool = True
) -> logging.Logger:
    """
    Configure and return logger instance.
    """
    logger = logging.getLogger(logger_name)

    # Prevent duplicate handlers if logger is already set up
    if len(logger.handlers) > 0:
        return logger  # Logger already configured

    logger.setLevel(log_level)
    formatter = logging.Formatter(log_format)

    # File logging
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_file_size, backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Console logging
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def setup_timed_logger(
    logger_name: str = "app",
    log_level: int = logging.INFO,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_file: str = None,
    when: str = "midnight",
    interval: int = 1,
    backup_count: int = 14,
    console_output: bool = True
) -> logging.Logger:
    """
    Configure a logger with time-based rotation.
    """
    logger = logging.getLogger(logger_name)

    if len(logger.handlers) > 0:
        return logger  # Logger already configured

    logger.setLevel(log_level)
    formatter = logging.Formatter(log_format)

    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = TimedRotatingFileHandler(
            log_file, when=when, interval=interval, backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


# Example usage
if __name__ == "__main__":
    app_logger = setup_logger("my_app", log_level=logging.DEBUG, log_file="logs/app.log")
    db_logger = setup_logger("my_app.database", log_level=logging.DEBUG, log_file="logs/database.log")

    app_logger.info("Application started")
    db_logger.debug("Database connection established")
