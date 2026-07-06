import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import json
from config.config import settings

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        # Include custom attributes if present
        if hasattr(record, "agent_name"):
            log_record["agent_name"] = record.agent_name
        if hasattr(record, "execution_time_ms"):
            log_record["execution_time_ms"] = record.execution_time_ms
        return json.dumps(log_record)

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Avoid duplicate handlers if logger is already initialized
    if logger.handlers:
        return logger

    # Console Handler (Human-readable)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File Handler (JSON structured for production)
    log_file = settings.LOGS_DIR / "chatbot.json.log"
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)

    return logger

# General application logger
app_logger = setup_logger("multi_agent_chatbot")
