# Deployed app

This repo includes `render.yaml` so it can be deployed to Render as a Blueprint after the GitHub repository is connected.

For a local demo:

```bash
python scripts/ingest.py --force
python -m src.app
```

- Web chat: http://127.0.0.1:5000/
- Health check: http://127.0.0.1:5000/health

If a public deployment is created, add the production URL here.
