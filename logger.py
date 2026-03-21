"""
logger.py
─────────
Appends one routing decision per line to a JSON Lines (.jsonl) file.

Each entry contains:
  timestamp      – ISO-8601 UTC timestamp
  user_message   – the original user input
  intent         – the classified (or overridden) intent label
  confidence     – the classifier confidence score [0.0 – 1.0]
  final_response – the text returned to the user
"""
import json
import os
from datetime import datetime, timezone

from config import LOG_FILE


def log_route(
    user_message: str,
    intent: str,
    confidence: float,
    final_response: str,
) -> None:
    """
    Append a routing record to the JSONL log file.

    The parent directory is created automatically if it doesn't exist,
    making this safe to call whether LOG_FILE is a relative path
    ('route_log.jsonl') or an absolute container path ('/app/logs/route_log.jsonl').
    """
    # Ensure the log directory exists (handles both relative and absolute paths)
    log_dir = os.path.dirname(os.path.abspath(LOG_FILE))
    os.makedirs(log_dir, exist_ok=True)

    entry = {
        "timestamp":      datetime.now(timezone.utc).isoformat(),
        "user_message":   user_message,
        "intent":         intent,
        "confidence":     round(confidence, 4),
        "final_response": final_response,
    }

    with open(LOG_FILE, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
