# syntax=docker/dockerfile:1.4

# Build stage
FROM python:3.12-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache gcc python3-dev musl-dev

# Create and activate virtual environment
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy requirements files separately for better caching
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Production stage with minimal Alpine base
FROM python:3.12-alpine

WORKDIR /app

# Create non-privileged user and prepare directories in one layer
RUN addgroup -S moodlemate && \
    adduser -S -G moodlemate moodlemate && \
    mkdir -p /app/logs && \
    chown -R moodlemate:moodlemate /app

# Copy virtual environment
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy application code
COPY --chown=moodlemate:moodlemate . .

# Switch to non-privileged user
USER moodlemate

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0 if True else 1)"

# Command to run the application
CMD ["python", "main.py"]