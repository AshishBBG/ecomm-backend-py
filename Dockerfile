# ---------- Build stage ----------
FROM python:3.11-slim AS builder

# Set build-time args for pip
ARG PIP_NO_CACHE_DIR=off
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# Install build deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install into a virtualenv-like location
COPY requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip wheel --no-deps --wheel-dir /wheels -r requirements.txt

# ---------- Final stage ----------
FROM python:3.11-slim

WORKDIR /app

# Create a non-root user
RUN groupadd -r app && useradd -r -g app -d /app -s /sbin/nologin app

# Install runtime deps and copy wheels
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels
RUN python -m pip install --upgrade pip && \
    pip install --no-deps --no-index --find-links /wheels -r /requirements.txt

# Copy app source
COPY . /app

# Ensure instance folder exists (if used)
RUN mkdir -p /app/instance && chown -R app:app /app

# Switch to non-root user
USER app

# Expose port (Railway sets PORT env at runtime)
EXPOSE 8000

# Healthcheck (optional--Railway may ignore Docker HEALTHCHECK)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Default command - Gunicorn binds to $PORT on Railway
CMD exec gunicorn "wsgi:app" -w 4 -k gthread -b 0.0.0.0:${PORT:-8000} --log-level info --access-logfile '-'
