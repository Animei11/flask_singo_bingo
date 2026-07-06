"""
Shared pytest fixtures for the whole test suite.

A "fixture" is just a function that sets something up (and optionally
tears it back down) so tests don't have to repeat that setup themselves.
Any test in this directory can use one of these just by naming it as a
parameter -- pytest sees the parameter name, looks for a fixture with
that name, runs it, and hands the test whatever it returns. You never
import these directly; pytest finds conftest.py automatically.
"""
import pytest

from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    """A Flask app configured for testing, with a fresh in-memory database.

    Each test gets its own empty set of tables (create_all/drop_all around
    the yield) so one test can never see rows left behind by another.
    """
    application = create_app()
    application.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",  # Flask sessions need *some* key to sign cookies
    )

    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A Flask test client: fires requests at the app in-process, no server needed."""
    return app.test_client()


class FakeRedis:
    """A minimal in-memory stand-in for redis.Redis.

    GameState only ever calls .get/.set/.exists/.delete, so that's all
    this needs to support. It stores whatever string game_service.py
    hands it (game_service does its own json.dumps/json.loads), so from
    game_service's point of view this behaves exactly like the real thing.
    """

    def __init__(self):
        self._store = {}

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value):
        self._store[key] = value

    def exists(self, key):
        return key in self._store

    def delete(self, key):
        self._store.pop(key, None)


@pytest.fixture
def fake_redis(monkeypatch):
    """Swap the real Redis client for an in-memory fake for one test.

    Important detail: game_service.py does
        from app.extensions import redis_client
    which binds the name `redis_client` *inside game_service's own module*
    at import time. Patching `app.extensions.redis_client` after that point
    wouldn't change what game_service.py sees -- it already has its own
    reference to the original object. The rule of thumb ("patch where a
    name is *used*, not where it's *defined*") is why this patches
    `app.services.game_service.redis_client` specifically.
    """
    fake = FakeRedis()
    monkeypatch.setattr("app.services.game_service.redis_client", fake)
    return fake
