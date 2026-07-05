# Overview: All Spotify logic
from app.music_player.base import MusicProvider


class SpotifyProvider(MusicProvider):
    def __init__(self, sp):
        self.sp = sp

    # TODO - Add logic to determine if there is an active device (and start one if not?)
    def is_active_device(self):
        pass

    def play_song(self, song_uri):
        self.sp.start_playback(uris=[song_uri])

    def stop_song(self):
        self.sp.pause_playback()

    def get_playlist_details(self, playlist_uri, playlist_id):
        playlist = self.sp.playlist(playlist_uri, fields="tracks.items(track(name,uri))")

        return [
            (item["track"]["uri"], item["track"]["name"], playlist_id)
            for item in playlist["tracks"]["items"]
            if item.get("track")
        ]
