"""
Unit tests for app/services/lobby_service.py.

The whole point of pulling the "singleplayer" -> 1 / else -> 8 mapping out
of the repository and into the service is that it's a business rule, not
a database detail -- so it should be testable without a database. These
tests mock lobby_repository the same way test_spotify_provider.py mocks
the spotipy client: the service under test never knows it's talking to a
fake.
"""
from unittest.mock import patch

from app.services import lobby_service


def test_create_lobby_maps_singleplayer_to_player_mode_one():
    with patch("app.services.lobby_service.lobby_repository") as fake_repo:
        lobby_service.create_lobby(
            lobby_code="ABCDE", player_mode="singleplayer", playlist_mode="classic"
        )

    fake_repo.create.assert_called_once_with(
        lobby_code="ABCDE", player_mode=1, playlist_mode="classic"
    )


def test_create_lobby_maps_anything_else_to_player_mode_eight():
    with patch("app.services.lobby_service.lobby_repository") as fake_repo:
        lobby_service.create_lobby(
            lobby_code="ABCDE", player_mode="multiplayer", playlist_mode="classic"
        )

    fake_repo.create.assert_called_once_with(
        lobby_code="ABCDE", player_mode=8, playlist_mode="classic"
    )


def test_generate_lobby_code_returns_five_letters():
    code = lobby_service.generate_lobby_code()

    assert len(code) == 5
    assert code.isalpha()
    assert code.isupper()
