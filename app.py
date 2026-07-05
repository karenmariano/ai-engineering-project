"""Render/Gunicorn compatibility entrypoint.

Some Render services default to `gunicorn app:app`. The real application lives
in `src.app`, so this module exposes the expected top-level Flask object.
"""

from src.app import create_app

app = create_app()

