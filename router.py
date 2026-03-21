"""
router.py
─────────
Implements route_and_respond(message, intent) – Step 2 of the pipeline.

Selects the correct expert system prompt based on the classified intent
and generates a final, context-aware response via a second LLM call.

Confidence threshold enforcement: if the classified confidence is below
CONFIDENCE_THRESHOLD, the intent is overridden to 'unclear' so the system
asks for clarification rather than guessing.
"""
from config import (
    get_client,
    MODEL_RESPONDER,
    CONFIDENCE_THRESHOLD,
    RESPONDER_TIMEOUT_SEC,
)
from prompts import SYSTEM_PROMPTS


def route_and_respond(message: str, intent: dict) -> str:
    """
    Route *message* to the appropriate expert persona and return the response.

    Parameters
    ----------
    message : str
        The original user message.
    intent  : dict
        Result from classify_intent(); must contain 'intent' and 'confidence'.

    Returns
    -------
    str
        The generated response text.
    """
    client = get_client()

    intent_label: str = intent.get("intent", "unclear")
    confidence: float = float(intent.get("confidence", 0.0))

    # ── Confidence threshold ──────────────────────────────────────────────────
    # If the classifier is not confident enough, fall back to 'unclear' and
    # ask for clarification rather than sending the request to the wrong persona.
    if confidence < CONFIDENCE_THRESHOLD and intent_label != "unclear":
        intent_label = "unclear"

    # ── Select system prompt ──────────────────────────────────────────────────
    system_prompt: str = SYSTEM_PROMPTS.get(intent_label, SYSTEM_PROMPTS["unclear"])

    # ── Generate response ─────────────────────────────────────────────────────
    try:
        response = get_client().chat.completions.create(
            model=MODEL_RESPONDER,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": message},
            ],
            temperature=0.7,
            max_tokens=800,
            timeout=RESPONDER_TIMEOUT_SEC,
        )
        return response.choices[0].message.content.strip()

    except Exception as exc:
        return f"An error occurred while generating a response: {exc}"
