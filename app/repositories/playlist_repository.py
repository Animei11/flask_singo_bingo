# Overview: All direct database access for the Playlist model. No business rules here.
from app.models.playlists import Playlist


def get_all():
    """ Returns every playlist row """
    return Playlist.query.all()
