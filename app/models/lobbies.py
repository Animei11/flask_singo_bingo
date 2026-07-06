from app.extensions import db
from sqlalchemy.sql import func


class Lobby(db.Model):
    __tablename__ = "lobbies"

    lobby_id = db.Column(db.Integer, primary_key=True)
    lobby_code = db.Column(db.String(6), nullable=False, unique=True)
    host_user_id = db.Column(
        db.Integer,
        db.ForeignKey("players.player_id", use_alter=True, name="fk_lobbies_host_user_id")
    )
    playlist_id = db.Column(db.Integer, db.ForeignKey("playlists.playlist_id"))
    playlist_mode = db.Column(db.String(20), nullable=False)
    player_mode = db.Column(db.Integer, nullable=True, server_default='8')
    status = db.Column(db.String(20), nullable=True, server_default='waiting', comment='waiting, active, or inactive')
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=True)
