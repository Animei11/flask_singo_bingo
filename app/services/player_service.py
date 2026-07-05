# Overview: Business rules for players/avatars. No SQLAlchemy/model imports here -- only the repositories.
from app.repositories import player_repository, avatar_repository


def add_player(username: str, lobby_code: str):
    return player_repository.add(username=username, lobby_code=lobby_code)


def get_avatar_list():
    """ Shapes Avatar rows into the {'id', 'filePath'} form the frontend expects """
    avatars = avatar_repository.get_all()
    return [
        {'id': avatar.avatar_id, 'filePath': 'static/imgs/avatars/' + avatar.avatar_file_name}
        for avatar in avatars
    ]


def assign_avatar_to_player(username: str, avatar_id: int):
    return player_repository.assign_avatar(username=username, avatar_id=avatar_id)


def mark_avatar_taken(avatar_id: int):
    return avatar_repository.mark_taken(avatar_id=avatar_id)


def get_player_avatar(username: str):
    return player_repository.get_avatar_for_username(username)
