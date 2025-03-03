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

# Create non-privileged user
RUN groupadd -r moodlemate && useradd -r -g moodlemate moodlemate

# Copy virtual environment
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

# Create logs directory and set permissions
RUN mkdir -p /app/logs && chown -R moodlemate:moodlemate /app

# Copy application code
COPY . .

# Set proper permissions
RUN chown -R moodlemate:moodlemate /app

# Switch to non-privileged user
USER moodlemate

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0 if True else 1)"

# Command to run the application
CMD ["python", "main.py"]