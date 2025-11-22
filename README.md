Production-ready scaffold generated from uploaded project.
- Factory pattern in `app/__init__.py`
- Extensions in `app/extensions.py`
- Error handlers in `app/errors.py`
- Routes registration in `app/routes/__init__.py`
- Run locally:
  1. python -m venv .venv
  2. source .venv/bin/activate  # or .\venv\Scripts\activate on Windows
  3. pip install -r requirements.txt
  4. export FLASK_APP=wsgi.py
  5. flask run
- Deployment:
  - Follow README_DEPLOY.md for Railway instructions.
