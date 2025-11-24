# ---------- Build stage ----------
FROM python:3.11-slim AS builder

# Set workdir
WORKDIR /app

# Install build deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc build-essential libpq-dev curl \
 && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (important for Docker layer caching)
COPY requirements.txt /app/requirements.txt

# Upgrade pip & build wheels for all requirements to speed final stage
RUN python -m pip install --upgrade pip setuptools wheel \
 && pip wheel --no-deps --wheel-dir /wheels -r /app/requirements.txt

# ---------- Final stage ----------
FROM python:3.11-slim

WORKDIR /app

# Create a non-root user for runtime
RUN groupadd -r app && useradd -r -g app -d /app -s /sbin/nologin app

# Install runtime dependencies (system libs required by some Python packages)
RUN apt-get update \
 && apt-get install -y --no-install-recommends libpq-dev curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Copy pre-built wheels and install into system site-packages
COPY --from=builder /wheels /wheels
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir --no-index --find-links /wheels -r /wheels/../requirements.txt || \
    pip install --no-cache-dir --no-index --find-links /wheels -r /app/requirements.txt

# Copy application source
COPY . /app

# Ensure instance folder exists and correct ownership
RUN mkdir -p /app/instance \
 && chown -R app:app /app

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Use entrypoint to run migrations safely before starting gunicorn (entrypoint.sh should be executable)
# If you don't have entrypoint.sh, the container will run the CMD directly.
ENTRYPOINT ["sh", "/app/entrypoint.sh"]

# Default command to start gunicorn (entrypoint should exec this or we fallback)
CMD ["gunicorn", "wsgi:app", "-w", "4", "-k", "gthread", "-b", "0.0.0.0:8000", "--log-level", "info"]
