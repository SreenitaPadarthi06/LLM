"""
classifier.py
─────────────
Implements classify_intent(message) – Step 1 of the routing pipeline.

Makes a short, low-cost LLM call and parses the JSON response into:
    {"intent": "<label>", "confidence": <float>}

Gracefully falls back to {"intent": "unclear", "confidence": 0.0} on
ANY error (network failure, malformed JSON, unexpected schema, etc.).
"""
import json
import re

from config import get_client, MODEL_CLASSIFIER, CLASSIFIER_TIMEOUT_SEC
from prompts import CLASSIFIER_PROMPT, SUPPORTED_INTENTS

# Safe fallback used whenever parsing or validation fails.
_FALLBACK: dict = {"intent": "unclear", "confidence": 0.0}


def classify_intent(message: str) -> dict:
    """
    Classify the intent of *message* using a lightweight LLM call.

    Returns
    -------
    dict
        {"intent": str, "confidence": float}
        intent is guaranteed to be one of SUPPORTED_INTENTS.
        confidence is guaranteed to be in [0.0, 1.0].
        Falls back to {"intent": "unclear", "confidence": 0.0} on error.
    """
    client = get_client()

    try:
        response = client.chat.completions.create(
            model=MODEL_CLASSIFIER,
            messages=[
                {"role": "system", "content": CLASSIFIER_PROMPT},
                {"role": "user",   "content": message},
            ],
            temperature=0.0,   # deterministic for classification
            max_tokens=60,     # JSON answer is tiny – keep cost minimal
            timeout=CLASSIFIER_TIMEOUT_SEC,
        )

        raw: str = response.choices[0].message.content.strip()

        # ── Extract JSON defensively ──────────────────────────────────────
        # The LLM might wrap output in markdown fences or add extra text.
        json_match = re.search(r"\{[^}]+\}", raw)
        if not json_match:
            return dict(_FALLBACK)

        parsed: dict = json.loads(json_match.group(0))

        # ── Validate & sanitise ───────────────────────────────────────────
        intent: str = str(parsed.get("intent", "unclear")).lower().strip()
        confidence: float = float(parsed.get("confidence", 0.0))

        if intent not in SUPPORTED_INTENTS:
            intent = "unclear"
            confidence = 0.0

        # Clamp confidence to [0.0, 1.0]
        confidence = max(0.0, min(1.0, confidence))

        return {"intent": intent, "confidence": confidence}

    except (json.JSONDecodeError, ValueError, KeyError, TypeError):
        # Malformed JSON or unexpected schema  → safe fallback
        return dict(_FALLBACK)
    except Exception:
        # Network error, API error, etc.       → safe fallback
        return dict(_FALLBACK)
