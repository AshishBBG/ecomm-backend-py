# Deploying to Railway (quick guide)

1. Create a new Railway project and connect your GitHub repo (or push the contents).
2. Add environment variables in Railway (DATABASE_URL, JWT_SECRET_KEY, SECRET_KEY).
3. Set the Start Command to: `gunicorn wsgi:app -w 4 -b 0.0.0.0:$PORT`
4. Railway will build the Dockerfile automatically. Ensure `requirements.txt` is present.
5. If using migrations, Railway must run `flask db upgrade` on deploy — entrypoint handles this when DATABASE_URL is set.
6. Set up Railway Postgres plugin and point DATABASE_URL to that database.
