# Overview: All direct database access for the Lobby model. No business rules here.
from app.extensions import db
from app.models.lobbies import Lobby


def get_by_code(lobby_code):
    """ Get lobby by lobby code """
    lobby = Lobby.query.filter_by(lobby_code=lobby_code).first()
    if not lobby:
        return "Error: Lobby not found"
    return lobby


def get_all_active_codes():
    """ Return all active lobbies """
    lobbies = Lobby.query.filter(Lobby.status != "inactive").all()
    return [lobby.lobby_code for lobby in lobbies]


def create(lobby_code: str, player_mode: int, playlist_mode: str):
    """ Creates lobby entry """
    lobby = Lobby(
        lobby_code=lobby_code,
        player_mode=player_mode,
        playlist_mode=playlist_mode
    )
    db.session.add(lobby)
    db.session.commit()


def add_playlist(lobby_code: str, playlist_id: int):
    """ Add playlist to lobby """
    lobby = Lobby.query.filter_by(lobby_code=lobby_code).first()
    if not lobby:
        return "Error: Lobby not found"
    lobby.playlist_id = playlist_id
    db.session.commit()
