import logging
import logging.config
import sys
from app.core.config import settings
from fastapi import FastAPI


# Logging configuration dictionary
log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s"
        },
        "json": {  # Structured JSON format for production
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "default",
            "level": "DEBUG"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 7,  # Keep 7 days of logs
            "formatter": "json",
            "level": "DEBUG"
        }
    },
    "loggers": {
        # "": {  # Root logger
        #     "handlers": ["console", "file"],
        #     "level": "INFO",
        #     "propagate": False
        # },
        "app": {  # Custom logger for your app
            "handlers": ["console", "file"],
            # "level": settings.log_level.upper() if settings.log_level else "DEBUG",
            "level": "DEBUG",
            "propagate": False
        },
        "uvicorn": {  # Uvicorn logger
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False
        }
    }
}

# Apply logging configuration
logging.config.dictConfig(log_config)

# Create logger
logger = logging.getLogger("app")