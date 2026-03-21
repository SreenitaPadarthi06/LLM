"""
main.py
───────
Entry point for the LLM-Powered Prompt Router.

Provides:
  process_message(message)  – full classify → route → log pipeline.
  run_cli()                  – interactive REPL.

Stretch-goal features included:
  • Confidence threshold   – intents below CONFIDENCE_THRESHOLD → 'unclear'.
  • Manual override prefix – "@<intent> <message>" bypasses the classifier.
"""
import re
import sys

from classifier import classify_intent
from logger import log_route
from prompts import SUPPORTED_INTENTS
from router import route_and_respond

# Matches "@intent actual message …" – override syntax
_OVERRIDE_RE = re.compile(r"^@(\w+)\s+(.+)$", re.DOTALL | re.IGNORECASE)

_BANNER = """
╔══════════════════════════════════════════════════════════════╗
║        LLM-Powered Prompt Router  —  Intent Classifier       ║
╠══════════════════════════════════════════════════════════════╣
║  Type a message and press Enter to classify & get a reply.   ║
║  Prefix with @<intent> to override routing, e.g.:            ║
║      @code   Fix this bug: for i in range(10) print(i)       ║
║      @data   Average of 10, 20, 30?                          ║
║      @writing  Is this sentence too long?                    ║
║      @career   Should I take this job offer?                 ║
║  Supported intents: code | data | writing | career | unclear ║
║  Type 'exit' or 'quit' to end the session.                   ║
╚══════════════════════════════════════════════════════════════╝
"""


# ── Core pipeline ─────────────────────────────────────────────────────────────

def process_message(message: str) -> dict:
    """
    Full routing pipeline for a single user message.

    Steps
    -----
    1. Check for manual @intent override prefix.
    2. If no override: call classify_intent().
    3. Call route_and_respond() with the (possibly overridden) intent.
    4. Append a record to route_log.jsonl via log_route().

    Returns
    -------
    dict with keys: intent (str), confidence (float),
                    response (str), override (bool)
    """
    stripped = message.strip()

    # ── Manual override ───────────────────────────────────────────────────────
    match = _OVERRIDE_RE.match(stripped)
    if match:
        override_label = match.group(1).lower()
        actual_message = match.group(2).strip()

        if override_label in SUPPORTED_INTENTS:
            intent_dict = {"intent": override_label, "confidence": 1.0}
            response = route_and_respond(actual_message, intent_dict)
            log_route(message, override_label, 1.0, response)
            return {
                "intent":     override_label,
                "confidence": 1.0,
                "response":   response,
                "override":   True,
            }
        # Unknown override label → fall through to normal classification

    # ── Normal two-step flow ──────────────────────────────────────────────────
    intent_dict = classify_intent(stripped)
    response    = route_and_respond(stripped, intent_dict)
    log_route(stripped, intent_dict["intent"], intent_dict["confidence"], response)

    return {
        "intent":     intent_dict["intent"],
        "confidence": intent_dict["confidence"],
        "response":   response,
        "override":   False,
    }


# ── Display helper ────────────────────────────────────────────────────────────

def _print_result(result: dict) -> None:
    """Pretty-print intent metadata and the generated response."""
    divider = "─" * 64
    tag = "  [MANUAL OVERRIDE]" if result.get("override") else ""
    print(f"\n{divider}")
    print(f"  Intent    : {result['intent'].upper()}{tag}")
    print(f"  Confidence: {result['confidence']:.2f}")
    print(divider)
    print(result["response"])
    print(f"{divider}\n")


# ── Interactive CLI ───────────────────────────────────────────────────────────

def run_cli() -> None:
    """Start the interactive prompt-router REPL."""
    print(_BANNER)
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSession ended.")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        result = process_message(user_input)
        _print_result(result)


# ── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Single-message mode: python main.py "how do I sort a list?"
        msg    = " ".join(sys.argv[1:])
        result = process_message(msg)
        _print_result(result)
    else:
        run_cli()
