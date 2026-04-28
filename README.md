# Lead Scoring App - GitHub and Render Ready

This package is prepared for deployment on Render.

## Files included
- `app.py` - Flask application
- `templates/` - HTML templates
- `requirements.txt` - Python dependencies
- `render.yaml` - Render Blueprint config
- `.python-version` - optional local/editor Python version pin
- `.gitignore` - Git ignore rules

## Local run
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## GitHub upload
1. Create a new GitHub repository.
2. Upload all files from this folder to the repo root.
3. Commit and push.

## Deploy on Render
### Option A: Blueprint deploy
1. Sign in to Render.
2. Create a new Blueprint.
3. Connect your GitHub repository.
4. Render will read `render.yaml`.
5. Deploy.

### Option B: Manual web service
Use these values:
- Runtime: Python 3
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

## Notes
- The app includes `/health` for Render health checks.
- The app binds to `0.0.0.0` and reads the `PORT` environment variable.
- `gunicorn` is included for production serving.
