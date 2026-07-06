from app.extensions import db


class PlayerStat(db.Model):
    __tablename__ = "player_stats"

    user_id = db.Column(db.Integer, db.ForeignKey("players.player_id"), primary_key=True)
    total_games = db.Column(db.Integer, nullable=True, server_default='0')
    wins = db.Column(db.Integer, nullable=True, server_default='0')
    losses = db.Column(db.Integer, nullable=True, server_default='0')
    win_rate = db.Column(db.Numeric(5, 2), nullable=True, server_default='0')
