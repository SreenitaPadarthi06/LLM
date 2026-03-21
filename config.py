"""
config.py
─────────
Centralised configuration: environment variables, model settings,
and a singleton OpenAI client factory.
"""
import os
from typing import Optional

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ── Model selection ────────────────────────────────────────────────────────────
MODEL_CLASSIFIER: str = os.getenv("MODEL_CLASSIFIER", "gpt-4o-mini")
MODEL_RESPONDER: str  = os.getenv("MODEL_RESPONDER",  "gpt-4o-mini")

# ── Routing settings ───────────────────────────────────────────────────────────
# Intents whose confidence falls below this threshold are treated as 'unclear'.
CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))

# API call timeouts in seconds to avoid hanging requests.
CLASSIFIER_TIMEOUT_SEC: float = float(os.getenv("CLASSIFIER_TIMEOUT_SEC", "20"))
RESPONDER_TIMEOUT_SEC: float = float(os.getenv("RESPONDER_TIMEOUT_SEC", "45"))

# ── Logging ────────────────────────────────────────────────────────────────────
LOG_FILE: str = os.getenv("LOG_FILE", "route_log.jsonl")

# ── OpenAI client (lazy singleton) ────────────────────────────────────────────
_client: Optional[OpenAI] = None


def get_client() -> OpenAI:
    """Return a shared OpenAI client, creating it on first call."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "OPENAI_API_KEY is not set. "
                "Copy .env.example to .env and add your API key."
            )
        _client = OpenAI(api_key=api_key)
    return _client
