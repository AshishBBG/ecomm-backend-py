# ---------- Build stage ----------
FROM python:3.11-slim AS builder

# Set workdir
WORKDIR /app

# Install build deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc build-essential libpq-dev curl \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements (must match your folder structure)
COPY requirements.txt /app/requirements.txt

# Upgrade pip & build wheels for all requirements
RUN python -m pip install --upgrade pip setuptools wheel \
 && pip wheel --no-deps --wheel-dir /wheels -r /app/requirements.txt


# ---------- Final stage ----------
FROM python:3.11-slim
WORKDIR /app

# Create non-root runtime user
RUN groupadd -r app && useradd -r -g app -d /app -s /sbin/nologin app

# Install runtime dependencies
RUN apt-get update \
 && apt-get install -y --no-install-recommends libpq-dev curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Copy wheels & install from them
COPY --from=builder /wheels /wheels
COPY requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir --no-index --find-links /wheels -r /app/requirements.txt

# Copy application code
COPY . /app

# Ensure instance folder exists
RUN mkdir -p /app/instance \
 && chown -R app:app /app

# Switch to non-root
USER app

# Expose port
EXPOSE 8000

# ENTRYPOINT to run migrations then start gunicorn
ENTRYPOINT ["sh", "/app/entrypoint.sh"]

# Default command used by entrypoint if no override
CMD ["gunicorn", "wsgi:app", "-w", "4", "-k", "gthread", "-b", "0.0.0.0:8000", "--log-level", "info"]
