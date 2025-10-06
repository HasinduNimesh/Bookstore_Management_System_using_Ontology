# Backend Dockerfile - Multi-stage build for smaller, safer runtime

# 1) Builder stage: compile wheels if needed
FROM python:3.11-bookworm AS builder
ENV PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update && apt-get -y upgrade && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN python -m pip install --upgrade pip && \
    pip wheel --wheel-dir=/wheels -r requirements.txt

# 2) Runtime stage: slim runtime with only wheels and app code
FROM python:3.11-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# Add a non-root user
RUN useradd -m appuser

# Install only built wheels (no compilers)
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/*
RUN apt-get update && apt-get -y upgrade && rm -rf /var/lib/apt/lists/*

# Copy application source
COPY . .

# Permissions
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
