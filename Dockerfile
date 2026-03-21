# ── Base image ────────────────────────────────────────────────────────────────
FROM python:3.11-slim

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /app

# ── Install Python dependencies first (layer-cached) ─────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application source ───────────────────────────────────────────────────
COPY . .

# ── Runtime configuration ─────────────────────────────────────────────────────
# Logs are written to /app/logs so they can be mounted as a host volume.
RUN mkdir -p /app/logs
ENV LOG_FILE=/app/logs/route_log.jsonl
ENV PYTHONUNBUFFERED=1

# ── Default command: interactive CLI ─────────────────────────────────────────
CMD ["python", "main.py"]
