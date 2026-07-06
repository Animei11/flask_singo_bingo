"""
Unit tests for app/services/lobby_service.py.

The whole point of pulling the "singleplayer" -> 1 / else -> 8 mapping out
of the repository and into the service is that it's a business rule, not
a database detail -- so it should be testable without a database. These
tests mock lobby_repository the same way test_spotify_provider.py mocks
the spotipy client: the service under test never knows it's talking to a
fake.
"""
from unittest.mock import patch, Mock

import pytest

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
    with patch("app.services.lobby_service.lobby_repository") as fake_repo:
        fake_repo.get_by_code.return_value = None  # no collision
        code = lobby_service.generate_lobby_code()

    assert len(code) == 5
    assert code.isalpha()
    assert code.isupper()


def test_generate_lobby_code_retries_on_collision():
    """ Regression test: lobbies.lobby_code is unique in the DB now, so a
    collision must be retried rather than passed straight through to a
    failed insert. """
    with patch("app.services.lobby_service.lobby_repository") as fake_repo, \
         patch("app.services.lobby_service.Faker") as fake_faker_cls:
        fake_faker_cls.return_value.bothify.side_effect = ["AAAAA", "BBBBB"]
        # First code is already taken (returns a Lobby-like object), second is free.
        fake_repo.get_by_code.side_effect = [Mock(), None]

        code = lobby_service.generate_lobby_code()

    assert code == "BBBBB"


def test_generate_lobby_code_gives_up_after_max_attempts():
    with patch("app.services.lobby_service.lobby_repository") as fake_repo:
        fake_repo.get_by_code.return_value = Mock()  # every attempt collides

        with pytest.raises(RuntimeError):
            lobby_service.generate_lobby_code()
