# LLM-Powered Prompt Router — Intent Classification

A Python service that intelligently routes user messages to specialised AI
personas using a **two-step Classify → Route** pipeline built on the OpenAI API.

---

## Architecture

```
User Message
     │
     ▼
classify_intent()          ← Step 1: fast, low-token LLM call (temp=0, max_tokens=60)
     │                        Returns: {"intent": "code", "confidence": 0.92}
     │
     ├─ "code"    ──► Code Expert persona        (production-quality code)
     ├─ "data"    ──► Data Analyst persona       (statistics & visualisation)
     ├─ "writing" ──► Writing Coach persona      (feedback, not rewrites)
     ├─ "career"  ──► Career Advisor persona     (actionable advice)
     └─ "unclear" ──► Asks a clarifying question
                  (also triggered when confidence < CONFIDENCE_THRESHOLD)
     │
     ▼
route_and_respond()        ← Step 2: expert system prompt + user message → response
     │
     ▼
Final Response  +  route_log.jsonl entry
```

---

## Project Structure

```
├── config.py          # Environment variables & OpenAI client singleton
├── prompts.py         # All prompts: classifier prompt + 5 expert personas
├── classifier.py      # classify_intent(message) → {"intent", "confidence"}
├── router.py          # route_and_respond(message, intent) → response str
├── logger.py          # log_route() → appends JSON Lines to route_log.jsonl
├── main.py            # process_message() orchestrator + interactive CLI
├── test_router.py     # Test suite: 16 sample messages + summary table
├── requirements.txt
├── .env.example
├── Dockerfile
└── docker-compose.yml
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and set your `OPENAI_API_KEY`.

### 3. Run the interactive CLI

```bash
python main.py
```

### 4. Single-message mode

```bash
python main.py "how do I sort a list in Python?"
```

### 5. Run the full test suite

```bash
python test_router.py
```

---

## Expert Personas

| Intent    | Persona        | Focus                                    |
| --------- | -------------- | ---------------------------------------- |
| `code`    | Code Expert    | Production-quality code, error handling  |
| `data`    | Data Analyst   | Statistics, correlations, visualisations |
| `writing` | Writing Coach  | Feedback on clarity/tone (no rewrites)   |
| `career`  | Career Advisor | Concrete, actionable career guidance     |
| `unclear` | Clarifier      | Single clarifying question to user       |

All prompts live in [`prompts.py`](prompts.py) — edit them there to customise
personas without touching business logic.

---

## Manual Override

Prefix any message with `@<intent>` to skip the classifier entirely:

```
@code   Fix this bug: for i in range(10) print(i)
@data   What can you tell me from: 12, 45, 23, 67, 34?
@writing  Is this sentence too verbose?
@career   Should I take this job offer?
```

---

## Confidence Threshold

If the classifier returns a confidence score **below** `CONFIDENCE_THRESHOLD`
(default `0.7`), the intent is overridden to `unclear` and the router asks for
clarification, regardless of the predicted label.

---

## Log Format

Every request is appended to `route_log.jsonl` (one JSON object per line):

```json
{
  "timestamp": "2026-03-11T12:00:00.000000+00:00",
  "user_message": "how do I sort a list in Python?",
  "intent": "code",
  "confidence": 0.97,
  "final_response": "Here is a Python example using `sorted()`:\n..."
}
```

---

## Configuration

| Variable               | Default           | Description                                |
| ---------------------- | ----------------- | ------------------------------------------ |
| `OPENAI_API_KEY`       | _(required)_      | Your OpenAI API key                        |
| `MODEL_CLASSIFIER`     | `gpt-4o-mini`     | Model used for intent classification       |
| `MODEL_RESPONDER`      | `gpt-4o-mini`     | Model used for generating final responses  |
| `CONFIDENCE_THRESHOLD` | `0.7`             | Below this, intent is treated as `unclear` |
| `LOG_FILE`             | `route_log.jsonl` | Path to the JSON Lines log file            |

---

## Docker

```bash
# Build the image
docker build -t prompt-router .

# Run the interactive CLI (mount logs to host)
docker run -it --env-file .env -v ${PWD}/logs:/app/logs prompt-router

# Or use Docker Compose
docker compose up                        # interactive CLI
docker compose --profile test run test   # test suite
```

---

## Core Requirements Checklist

| #   | Requirement                                        | Status |
| --- | -------------------------------------------------- | ------ |
| 1   | ≥ 4 distinct expert system prompts in config       | ✓      |
| 2   | `classify_intent()` returns `{intent, confidence}` | ✓      |
| 3   | `route_and_respond()` maps intent → expert call    | ✓      |
| 4   | `unclear` intent → clarifying question, no guess   | ✓      |
| 5   | All requests logged to `route_log.jsonl`           | ✓      |
| 6   | Malformed JSON from classifier → graceful fallback | ✓      |

## Stretch Goals Implemented

| Feature              | Implementation                                          |
| -------------------- | ------------------------------------------------------- |
| Confidence threshold | `CONFIDENCE_THRESHOLD` env var, enforced in `router.py` |
| Manual override      | `@intent message` prefix, detected in `main.py`         |
| CLI with metadata    | Intent label + confidence displayed for every response  |
