# ---------- build stage ----------
FROM python:3.11-slim AS build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# Install build dependencies required to compile wheels for some packages (cryptography, psycopg2)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       libffi-dev \
       libssl-dev \
       libpq-dev \
       curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Upgrade pip & install deps
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# ---------- runtime stage ----------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install minimal runtime dependencies (libpq runtime library for psycopg2; libssl for cryptography)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libpq5 \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create an unprivileged user
RUN useradd --system --create-home --home-dir /home/appuser appuser

# Copy installed Python packages from build stage
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copy application source
COPY . .

# Ensure runtime scripts are executable
RUN chmod +x ./entrypoint.sh || true

# Make sure source files are not writable by other users (optional)
RUN chown -R appuser:appuser /app

USER appuser

# Expose the port Railway will provide (this is informational)
EXPOSE 5000

# Use the entrypoint script which will run migrations and start Gunicorn
# Entry point will use $PORT if provided by Railway
CMD ["./entrypoint.sh"]
