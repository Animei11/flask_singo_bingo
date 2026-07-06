# Overview: Abstract interface implemented by all music providers
from abc import ABC, abstractmethod


class MusicProvider(ABC):
    @abstractmethod
    def is_active_device(self) -> bool:
        pass

    @abstractmethod
    def play_song(self, song_uri: str) -> None:
        pass

    @abstractmethod
    def stop_song(self) -> None:
        pass

    @abstractmethod
    def get_playlist_details(self, playlist_uri, playlist_id) -> list[tuple]:
        pass
