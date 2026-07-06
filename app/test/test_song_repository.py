"""
Regression test for a real bug: get_playlist_details (SpotifyProvider) has
always produced 3-tuples (uri, name, playlist_id), but add_all_if_missing
used to unpack 2-tuples out of that same list -- a ValueError waiting to
fire the first time any playlist's songs got inserted. This test locks in
the fix: 3-tuple input must not raise, and must build the right rows.
"""
from unittest.mock import MagicMock, patch

from app.repositories import song_repository


def test_add_all_if_missing_accepts_three_tuples_without_raising():
    playlist_details = [
        ("spotify:track:1", "Song One", 7),
        ("spotify:track:2", "Song Two", 7),
    ]

    with patch("app.repositories.song_repository.db") as fake_db, \
         patch("app.repositories.song_repository.execute_values") as fake_execute_values:
        # Simulate "no songs for this playlist yet" so the insert branch runs.
        fake_db.session.execute.return_value.fetchone.return_value = None
        fake_cursor = MagicMock()
        fake_conn = fake_db.session.connection.return_value.connection
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor

        song_repository.add_all_if_missing(playlist_details, playlist_id=7)

    fake_execute_values.assert_called_once()
    _, call_args, _ = fake_execute_values.mock_calls[0]
    inserted_rows = call_args[2]
    assert inserted_rows == [
        ("spotify:track:1", "Song One", 7),
        ("spotify:track:2", "Song Two", 7),
    ]


def test_add_all_if_missing_skips_insert_when_songs_already_exist():
    with patch("app.repositories.song_repository.db") as fake_db, \
         patch("app.repositories.song_repository.execute_values") as fake_execute_values:
        fake_db.session.execute.return_value.fetchone.return_value = (1,)

        song_repository.add_all_if_missing([("uri", "name", 7)], playlist_id=7)

    fake_execute_values.assert_not_called()
