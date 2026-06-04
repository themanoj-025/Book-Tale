"""
config.py - Centralized configuration with .env support
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration - all tunable constants in one place."""

    # ── Loan & Fine Settings ────────────────────────────────────
    ISSUE_DAYS: int = int(os.getenv("ISSUE_DAYS", "14"))
    FINE_PER_DAY: float = float(os.getenv("FINE_PER_DAY", "5.0"))
    MAX_BORROW_LIMIT: int = int(os.getenv("MAX_BORROW_LIMIT", "3"))
    MEMBERSHIP_VALIDITY_DAYS: int = int(os.getenv("MEMBERSHIP_VALIDITY_DAYS", "365"))

    # ── Data Directories ────────────────────────────────────────
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    LOGS_DIR: str = os.path.join(BASE_DIR, "logs")
    BACKUPS_DIR: str = os.path.join(BASE_DIR, "backups")
    UPLOADS_DIR: str = os.path.join(BASE_DIR, "uploads")

    # ── Upload Settings ─────────────────────────────────────────
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", str(5 * 1024 * 1024)))  # 5 MB
    ALLOWED_EXTENSIONS: set = set(os.getenv("ALLOWED_EXTENSIONS", ".jpg,.jpeg,.png,.gif,.webp").split(","))

    # ── JSON Data Files ─────────────────────────────────────────
    BOOKS_FILE: str = os.path.join(DATA_DIR, "books.json")
    USERS_FILE: str = os.path.join(DATA_DIR, "users.json")
    TRANSACTIONS_FILE: str = os.path.join(DATA_DIR, "transactions.json")
    RESERVATIONS_FILE: str = os.path.join(DATA_DIR, "reservations.json")
    FINES_FILE: str = os.path.join(DATA_DIR, "fines.json")
    NOTIFICATIONS_FILE: str = os.path.join(DATA_DIR, "notifications.json")

    # ── Logging ─────────────────────────────────────────────────
    LOG_FILE: str = os.path.join(LOGS_DIR, "activity.log")
    JSON_LOG: str = os.path.join(LOGS_DIR, "activity.json")

    # ── Default Admin ───────────────────────────────────────────
    DEFAULT_ADMIN_ID: str = os.getenv("DEFAULT_ADMIN_ID", "ADMIN001")
    DEFAULT_ADMIN_PASSWORD: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")

    # ── Web Server ──────────────────────────────────────────────
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
    FLASK_HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    # ── OpenLibrary API ─────────────────────────────────────────
    OPENLIBRARY_BASE_URL: str = "https://openlibrary.org"

    # ── SMTP Email Settings ─────────────────────────────────────
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "noreply@libraryms.com")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "True").lower() == "true"
    LIBRARY_NAME: str = os.getenv("LIBRARY_NAME", "Library Management System")

    # ── Settings Override File ──────────────────────────────────
    # Load settings from settings_override.json (written by admin settings UI)
    _override_path = os.path.join(DATA_DIR, "settings_override.json")
    if os.path.exists(_override_path):
        try:
            import json as _json
            with open(_override_path, "r") as _f:
                _overrides = _json.load(_f)
            for _key, _val in _overrides.items():
                if hasattr(Config, _key):
                    _attr_type = type(getattr(Config, _key))
                    if _attr_type == bool:
                        setattr(Config, _key, str(_val).lower() == "true")
                    elif _attr_type == int:
                        try: setattr(Config, _key, int(_val))
                        except: pass
                    elif _attr_type == float:
                        try: setattr(Config, _key, float(_val))
                        except: pass
                    elif _attr_type == set:
                        setattr(Config, _key, set(str(_val).split(",")) if isinstance(_val, str) else _val)
                    else:
                        setattr(Config, _key, _val)
        except Exception as _e:
            import sys as _sys
            print("[Config] Warning: Could not load settings override:", _e, file=_sys.stderr)

    EMAIL_NOTIFICATIONS_ENABLED: bool = os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "True").lower() == "true"
