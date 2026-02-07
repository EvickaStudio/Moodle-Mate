# syntax=docker/dockerfile:1.4

# Build stage
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-slim-bookworm

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/*

# Create non-privileged user
RUN groupadd -r moodlemate && useradd -r -g moodlemate moodlemate

# Copy virtual environment
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

# Create directories needed before volumes mount
RUN mkdir -p /app/logs /app/state

# Copy application code
COPY . .

# Copy entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import os, urllib.request; enabled=os.getenv('MOODLEMATE_WEB__ENABLED', 'true').lower() not in {'0','false','no'}; port=int(os.getenv('MOODLEMATE_WEB__PORT', '9095')); urllib.request.urlopen(f'http://127.0.0.1:{port}/healthz', timeout=3) if enabled else 0"

# Entrypoint ensures permissions then drops to non-root user
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-m", "moodlemate"]
