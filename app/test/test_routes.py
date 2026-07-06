"""
Integration tests: these go through the real Flask routing layer and a
real (in-memory) database, unlike test_game_service.py and
test_spotify_provider.py, which each isolate one class. Integration tests
catch a different category of bug -- "does the route actually wire these
pieces together correctly" -- at the cost of being slower and telling you
less precisely where a failure came from. Good suites have both kinds.
"""
import pytest

from app.extensions import db
from app.models.lobbies import Lobby
from app.models.playlists import Playlist
from app.services.game_service import GameState


def test_create_lobby_persists_a_row_and_creates_matching_game_state(client, fake_redis):
    response = client.post(
        "/db/createLobby",
        json={"player_mode": "singleplayer", "playlist_mode": "classic"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["ok"] is True
    lobby_code = body["lobby_code"]

    # The route should have written a matching row to the database...
    assert Lobby.query.filter_by(lobby_code=lobby_code).first() is not None

    # ...and created matching game state (in fake_redis, standing in for Redis).
    state = GameState.get_game(lobby_code).get_state()
    assert state["status"] == "waiting"


def test_create_lobby_rejects_missing_fields(client, fake_redis):
    response = client.post("/db/createLobby", json={"player_mode": "singleplayer"})

    assert response.status_code == 400
    assert response.get_json()["ok"] is False


def test_get_playlists_returns_seeded_playlists(client, app):
    with app.app_context():
        db.session.add(Playlist(playlist_uri="uri-1", playlist_name="My Mix"))
        db.session.commit()

    response = client.get("/spotify/getplaylists")

    assert response.status_code == 200
    playlists = response.get_json()
    assert len(playlists) == 1
    assert playlists[0]["playlist_name"] == "My Mix"


# Regression tests for a real bug: lobby_repository.get_by_code used to
# return the string "Error: Lobby not found" instead of None, and a
# non-empty string is truthy -- so these routes' `if not lobby_exists`
# checks never fired for a lobby that was never created.
def test_lobby_page_404s_for_unknown_lobby_code(client):
    response = client.get("/lobby/NOPE")

    assert response.status_code == 404


def test_start_game_404s_for_unknown_lobby_code(client):
    response = client.get("/startGame/NOPE")

    assert response.status_code == 404


def test_game_over_404s_for_unknown_lobby_code(client):
    response = client.get("/gameOver/NOPE")

    assert response.status_code == 404


# Regression test for a real bug: require_spotify used to catch bare
# `except Exception`, so a totally unrelated bug inside get_spotify_client
# would get reported to the client as "please log in" instead of surfacing.
def test_require_spotify_lets_unexpected_errors_propagate(client, monkeypatch):
    with client.session_transaction() as sess:
        sess["spotify_token"] = {"access_token": "x"}

    monkeypatch.setattr(
        "app.music_player.spotify.decorator.get_spotify_client",
        lambda token: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    with pytest.raises(RuntimeError):
        client.get("/spotify/playlists/playsong?song_uri=spotify:track:1")
