"""
logger.py - Command/action logging system
"""

import os
import json
from datetime import datetime
from typing import List

from config import Config


def log(action: str, actor: str = "System", extra: str = "") -> None:
    """Log an action to both text and JSON log files."""
    os.makedirs(Config.LOGS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{actor}] {action}"
    if extra:
        line += f" | {extra}"

    # Append to text log
    with open(Config.LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

    # Append to JSON log
    entry = {"timestamp": ts, "actor": actor, "action": action, "extra": extra}
    entries: list = []
    if os.path.exists(Config.JSON_LOG):
        try:
            with open(Config.JSON_LOG, "r", encoding="utf-8") as f:
                entries = json.load(f)
        except Exception:
            entries = []
    entries.append(entry)
    with open(Config.JSON_LOG, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)


def get_logs(limit: int = 50) -> List[str]:
    """Get the last N log lines from the text log file."""
    if not os.path.exists(Config.LOG_FILE):
        return []
    with open(Config.LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [l.strip() for l in lines[-limit:]]
