"""
Unit tests for app/services/player_service.py.

get_avatar_list()'s only real job is shaping Avatar rows into the exact
dict shape the frontend already expects (see app/static/js/login.js,
which reads avatar.filePath and avatar.id). That shaping is the piece
that used to live inside the query function -- now it's isolated and
testable without a database, using a fake in place of an Avatar row.
"""
from unittest.mock import patch, Mock

from app.services import player_service


def test_get_avatar_list_shapes_avatar_rows_into_id_and_file_path():
    fake_avatar = Mock(avatar_id=3, avatar_file_name="alien.png")

    with patch("app.services.player_service.avatar_repository") as fake_repo:
        fake_repo.get_all.return_value = [fake_avatar]
        result = player_service.get_avatar_list()

    assert result == [{"id": 3, "filePath": "static/imgs/avatars/alien.png"}]
