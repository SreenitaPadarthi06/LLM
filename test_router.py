"""
test_router.py
──────────────
Runs the prompt router against the 16 sample messages specified in the task
(plus the manual-override stretch-goal case) and prints a formatted summary.

All results are also appended to route_log.jsonl via the normal log_route()
path inside process_message(), so the log file grows with each test run.

Usage
─────
    python test_router.py
"""
from main import process_message

# ── Test cases ────────────────────────────────────────────────────────────────
# Format: (message, expected_intent_hint)
# The hint is INFORMATIONAL only – the LLM is the source of truth.
# Mismatches are noted but do NOT count as hard failures.
TEST_CASES = [
    # ── Clear-intent messages ─────────────────────────────────────────────
    ("how do i sort a list of objects in python?",                        "code"),
    ("explain this sql query for me",                                     "data"),
    ("This paragraph sounds awkward, can you help me fix it?",            "writing"),
    ("I'm preparing for a job interview, any tips?",                      "career"),
    ("what's the average of these numbers: 12, 45, 23, 67, 34",          "data"),
    ("what is a pivot table",                                             "data"),
    ("fxi thsi bug pls: for i in range(10) print(i)",                     "code"),
    ("How do I structure a cover letter?",                                "career"),
    ("My boss says my writing is too verbose.",                           "writing"),
    ("Rewrite this sentence to be more professional.",                    "writing"),
    ("I'm not sure what to do with my career.",                           "career"),

    # ── Ambiguous / unclear messages ─────────────────────────────────────
    ("Help me make this better.",                                         "unclear"),
    (
        "I need to write a function that takes a user id and returns "
        "their profile, but also i need help with my resume.",
        "unclear",
    ),
    ("hey",                                                               "unclear"),
    ("Can you write me a poem about clouds?",                             "unclear"),

    # ── Stretch goal: manual @intent override ────────────────────────────
    ("@code Fix this bug: def add(a,b) return a+b",                       "code"),
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def _truncate(text: str, n: int = 55) -> str:
    return text[:n] + "…" if len(text) > n else text


def _match_symbol(got: str, expected: str) -> str:
    """Return a display symbol based on whether intent matched the hint."""
    if got == expected:
        return "OK "
    if expected == "unclear":
        # Ambiguous cases: any result is acceptable
        return " ? "
    return "~  "


# ── Test runner ───────────────────────────────────────────────────────────────

def run_tests() -> None:
    width = 72
    print("\n" + "=" * width)
    print("  PROMPT ROUTER — TEST SUITE  ({} test cases)".format(len(TEST_CASES)))
    print("=" * width)
    print(
        f"  {'#':<4} {'Hint':<9} {'Got':<9} {'Conf':>5}  {'OK?':<4}  Message"
    )
    print("-" * width)

    results = []
    for idx, (message, expected) in enumerate(TEST_CASES, 1):
        try:
            result   = process_message(message)
            got      = result["intent"]
            conf     = result["confidence"]
            override = result.get("override", False)
            symbol   = _match_symbol(got, expected)
            ovr_tag  = " [OVR]" if override else ""

            print(
                f"  {idx:<4} {expected:<9} {got:<9} {conf:>5.2f}  {symbol}   "
                f"{_truncate(message)}{ovr_tag}"
            )
            results.append(
                {
                    "test":     idx,
                    "message":  message,
                    "expected": expected,
                    "intent":   got,
                    "confidence": conf,
                    "override": override,
                    "error":    None,
                }
            )

        except Exception as exc:
            print(f"  {idx:<4} {'ERROR':<9} {str(exc)[:55]}")
            results.append(
                {
                    "test":    idx,
                    "message": message,
                    "error":   str(exc),
                }
            )

    # ── Summary ───────────────────────────────────────────────────────────────
    print("=" * width)
    total   = len(TEST_CASES)
    errors  = sum(1 for r in results if r.get("error"))
    matched = sum(
        1 for r in results
        if not r.get("error") and r["intent"] == r["expected"]
    )
    print(f"\n  Total tests  : {total}")
    print(f"  Matched hint : {matched}  (informational – LLM is authoritative)")
    print(f"  Errors       : {errors}")
    print(
        "\n  NOTE  Ambiguous inputs (marked '?') may legitimately differ from "
        "the hint.\n        'OK' = intent matched hint; '~' = differs from hint; "
        "'?' = hint was 'unclear'."
    )
    print("=" * width + "\n")


if __name__ == "__main__":
    run_tests()
