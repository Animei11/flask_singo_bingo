# Overview: All direct database access for the Avatar model. No business rules here.
from app.extensions import db
from app.models.avatars import Avatar


def get_all():
    """ Select all avatars and return them """
    return Avatar.query.all()


def mark_taken(avatar_id: int):
    """ Mark avatar as chosen """
    avatar = Avatar.query.get(avatar_id)
    if avatar:
        avatar.taken = 1
        db.session.commit()
