from faker import Faker
from app.extensions import db
from app.models.lobbies import Lobby

# TODO: Add a trigger to know when a user is added to that lobby for the circle of avatars to display
""" Generates lobby code with 5 letters """
def generate_lobby_code():
    faker = Faker()
    lobby_code = faker.bothify(text='?????', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    print(f'Generated Lobby Code: {lobby_code}')
    return lobby_code

""" Get lobby by lobby code """
def db_get_lobby(lobby_code):
    lobby = Lobby.query.filter_by(lobby_code=lobby_code).first()
    if not lobby:
        return "Error: Lobby not found"
    return lobby

""" Return all active lobbies """
def db_get_all_active_lobbies():
    lobbies = Lobby.query.filter(Lobby.status!="inactive").all()
    list_of_lobbies = [lobby.lobby_code for lobby in lobbies]
    return list_of_lobbies

""" Creates lobby entry """
def db_create_lobby(lobby_code: str, player_mode: str, playlist_mode: str):
    lobby = Lobby(
        lobby_code=lobby_code,
        player_mode= 1 if player_mode == "singleplayer" else 8,
        playlist_mode=playlist_mode
    )
    db.session.add(lobby)
    db.session.commit()

""" Add playlist to lobby """
def db_add_playlist_to_lobby(lobby_code: str, playlist_id: int):
    lobby = Lobby.query.filter_by(lobby_code=lobby_code).first()
    if not lobby:
        return "Error: Lobby not found"
    lobby.playlist_id = playlist_id
    db.session.commit()