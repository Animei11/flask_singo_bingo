# Overview: Business rules for lobbies. No SQLAlchemy/model imports here -- only the repository.
from faker import Faker
from app.repositories import lobby_repository

MAX_LOBBY_CODE_ATTEMPTS = 10

# TODO: Add a trigger to know when a user is added to that lobby for the circle of avatars to display
""" Generates a lobby code with 5 letters, retrying if it collides with an existing lobby """
def generate_lobby_code():
    faker = Faker()
    for _ in range(MAX_LOBBY_CODE_ATTEMPTS):
        lobby_code = faker.bothify(text='?????', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        if lobby_repository.get_by_code(lobby_code) is None:
            print(f'Generated Lobby Code: {lobby_code}')
            return lobby_code
    raise RuntimeError("Could not generate a unique lobby code after several attempts")


def get_lobby(lobby_code):
    return lobby_repository.get_by_code(lobby_code)


def get_all_active_lobbies():
    return lobby_repository.get_all_active_codes()


def create_lobby(lobby_code: str, player_mode: str, playlist_mode: str):
    """ Turns the player_mode label into the stored player count, then persists the lobby """
    player_count = 1 if player_mode == "singleplayer" else 8
    lobby_repository.create(lobby_code=lobby_code, player_mode=player_count, playlist_mode=playlist_mode)


def add_playlist_to_lobby(lobby_code: str, playlist_id: int):
    return lobby_repository.add_playlist(lobby_code=lobby_code, playlist_id=playlist_id)
