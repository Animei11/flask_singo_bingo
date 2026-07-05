"""
Unit tests for app/services/playlist_service.py.

get_playlists()'s "classic mode -> shuffle and keep only 4" rule used to
be interleaved with the query that fetches every playlist row. Now that
it's separated, we can prove the rule itself without touching a database:
mock playlist_repository to return five fixed playlists and check what
get_playlists does with them.
"""
from unittest.mock import patch, Mock

from app.services import playlist_service


def _fake_playlists(count):
    return [
        Mock(playlist_id=i, playlist_uri=f"uri-{i}", playlist_name=f"Playlist {i}")
        for i in range(count)
    ]


def test_classic_mode_returns_at_most_four_playlists():
    with patch("app.services.playlist_service.playlist_repository") as fake_repo:
        fake_repo.get_all.return_value = _fake_playlists(10)
        result = playlist_service.get_playlists(playlist_mode="classic")

    assert len(result) == 4


def test_non_classic_mode_returns_every_playlist():
    with patch("app.services.playlist_service.playlist_repository") as fake_repo:
        fake_repo.get_all.return_value = _fake_playlists(10)
        result = playlist_service.get_playlists(playlist_mode=None)

    assert len(result) == 10


def test_playlists_are_shaped_into_id_uri_and_name():
    with patch("app.services.playlist_service.playlist_repository") as fake_repo:
        fake_repo.get_all.return_value = _fake_playlists(1)
        result = playlist_service.get_playlists(playlist_mode=None)

    assert result == [{"id": 0, "playlist_uri": "uri-0", "playlist_name": "Playlist 0"}]
