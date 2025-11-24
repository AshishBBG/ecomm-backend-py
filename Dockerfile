FROM python:3.11-slim

WORKDIR /app

# system deps for some packages (MySQL/Postgres libs if needed)
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc build-essential libpq-dev curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements into correct path and install
COPY requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r /app/requirements.txt

# Copy application source
COPY . /app

# Ensure instance folder exists
RUN mkdir -p /app/instance

# Use non-root user (optional)
RUN groupadd -r app && useradd -r -g app -d /app -s /sbin/nologin app \
 && chown -R app:app /app

USER app

EXPOSE 8000

ENTRYPOINT ["sh", "/app/entrypoint.sh"]
CMD ["gunicorn", "wsgi:app", "-w", "4", "-k", "gthread", "-b", "0.0.0.0:8000", "--log-level", "info"]
