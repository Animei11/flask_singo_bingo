from app.extensions import db


class Playlist(db.Model):
    __tablename__ = "playlists"

    playlist_id = db.Column(db.Integer, primary_key=True)
    playlist_uri = db.Column(db.String(100), nullable=False)
    playlist_name = db.Column(db.String(100), nullable=False)
