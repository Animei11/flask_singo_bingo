"""
Unit tests for SpotifyProvider (app/music_player/spotify/service.py).

This is the concrete payoff of introducing the MusicProvider interface:
SpotifyProvider only ever calls methods on `self.sp`, and never cares
whether `self.sp` is a real spotipy.Spotify client or a plain
unittest.mock.Mock(). That means we can test our URI-building and
response-parsing logic completely offline -- no Spotify account, no
network call, no access token, no rate limits -- by handing it a Mock
and asserting how SpotifyProvider used it.
"""
from unittest.mock import Mock

from app.music_player.spotify.service import SpotifyProvider


def test_play_song_starts_playback_with_the_given_uri():
    sp = Mock()
    provider = SpotifyProvider(sp)

    provider.play_song("spotify:track:abc123")

    sp.start_playback.assert_called_once_with(uris=["spotify:track:abc123"])


def test_stop_song_pauses_playback():
    sp = Mock()
    provider = SpotifyProvider(sp)

    provider.stop_song()

    sp.pause_playback.assert_called_once()


def test_get_playlist_details_returns_uri_name_playlist_id_tuples():
    sp = Mock()
    # This is a trimmed-down version of the shape Spotify's API actually
    # returns for the fields we request -- see the `fields=` kwarg in
    # SpotifyProvider.get_playlist_details.
    sp.playlist.return_value = {
        "tracks": {
            "items": [
                {"track": {"uri": "spotify:track:1", "name": "Song One"}},
                {"track": {"uri": "spotify:track:2", "name": "Song Two"}},
            ]
        }
    }
    provider = SpotifyProvider(sp)

    details = provider.get_playlist_details(playlist_uri="spotify:playlist:xyz", playlist_id=7)

    assert details == [
        ("spotify:track:1", "Song One", 7),
        ("spotify:track:2", "Song Two", 7),
    ]
    sp.playlist.assert_called_once_with(
        "spotify:playlist:xyz", fields="tracks.items(track(name,uri))"
    )


def test_get_playlist_details_skips_items_with_no_track():
    """Spotify returns a null 'track' for songs that were removed from the
    catalog or are local-only files it can't serve -- get_playlist_details
    should skip those instead of raising a KeyError/TypeError."""
    sp = Mock()
    sp.playlist.return_value = {
        "tracks": {
            "items": [
                {"track": {"uri": "spotify:track:1", "name": "Song One"}},
                {"track": None},
            ]
        }
    }
    provider = SpotifyProvider(sp)

    details = provider.get_playlist_details(playlist_uri="spotify:playlist:xyz", playlist_id=7)

    assert details == [("spotify:track:1", "Song One", 7)]
