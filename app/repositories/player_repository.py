# Overview: All direct database access for the Player model. No business rules here.
from sqlalchemy import func
from app.extensions import db
from app.models.players import Player
from app.models.avatars import Avatar


def add(username: str, lobby_code: str):
    """ Add a new player to players db """
    player = Player(username=username, lobby_code=lobby_code)
    db.session.add(player)
    db.session.commit()


def assign_avatar(username: str, avatar_id: int):
    """ Add chosen avatar to existing player in players db """
    player = Player.query.filter(func.lower(Player.username) == username.lower()).first()
    if player:
        player.avatar_id = avatar_id
        db.session.commit()


def get_avatar_for_username(username: str):
    """ Return the Avatar belonging to the player with this username, or None """
    player = Player.query.filter(func.lower(Player.username) == username.lower()).first()
    print(f"Queried player: {player}")
    if player and player.avatar_id:
        avatar = Avatar.query.get(player.avatar_id)
        return avatar
    return None
