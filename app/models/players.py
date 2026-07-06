from app.extensions import db
from sqlalchemy.sql import func


class Player(db.Model):
    __tablename__ = "players"

    player_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    avatar_id = db.Column(db.Integer, db.ForeignKey("avatars.avatar_id"))
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=True)
    lobby_code = db.Column(db.String(6), db.ForeignKey("lobbies.lobby_code"))
    status = db.Column(db.Text, nullable=False, server_default='active', comment='active or inactive')
