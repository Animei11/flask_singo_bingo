from app.extensions import db

class Song(db.Model):
    __tablename__ = "songs"

    song_id = db.Column(db.Integer, primary_key=True)
    song_uri = db.Column(db.String(255), nullable=False)
    song_name = db.Column(db.String(255), nullable=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey("playlists.playlist_id"))

    def to_dict(self):
        return {
            "song_id": self.song_id,
            "song_uri": self.song_uri,
            "song_name": self.song_name,
            "playlist_id": self.playlist_id
        }
