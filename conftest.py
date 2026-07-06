"""
Root-level conftest.py. This file has exactly one job: set DATABASE_URL
before anything else in the project gets imported.

Why this can't just live in app/test/conftest.py (where the rest of the
fixtures are): app/test/ has an __init__.py, which makes it a real
sub-package. To import app.test.conftest, Python is *required* to fully
import the `app` package first -- and app/__init__.py does
`from app.config import Config` at its own top level (not inside
create_app()). That line reads os.getenv("DATABASE_URL") the moment the
`app` package is imported, which happens before app/test/conftest.py's
own code has a chance to run. Whatever DATABASE_URL was (or wasn't) set
to in the real shell environment gets locked in at that point.

This file has no parent package above it, so pytest loads it as a bare
top-level module before touching `app` at all -- which is early enough.
"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
