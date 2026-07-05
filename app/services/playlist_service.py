# Overview: Business rules for playlists/songs. No SQLAlchemy/model imports here -- only the repositories.
import random
from app.repositories import playlist_repository, song_repository


def get_playlists(playlist_mode: str = None):
    """ Returns a list of playlists depending on what mode is put in param
        DEFAULT: Return all
    """
    # TODO: Add different modes as fit
    playlists = playlist_repository.get_all()
    playlists_list = [{"id": playlist.playlist_id,
                       "playlist_uri": playlist.playlist_uri,
                       "playlist_name": playlist.playlist_name
                       } for playlist in playlists]
    if playlist_mode == 'classic':
        random.shuffle(playlists_list)
        playlists_list = playlists_list[:4]
    return playlists_list


def add_all_songs(playlist_details, playlist_id):
    return song_repository.add_all_if_missing(playlist_details, playlist_id)


def get_songs_for_bingo_card(lobby_code):
    return song_repository.get_for_lobby(lobby_code)
