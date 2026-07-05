from functools import wraps
from flask import session, jsonify, g
from app.music_player.spotify.oauth import get_spotify_client
from app.music_player.spotify.service import SpotifyProvider

def require_spotify(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = session.get("spotify_token")
        if not token:
            return jsonify({"auth_required": True}), 401

        try:
            g.music_provider = SpotifyProvider(get_spotify_client(token))
        except Exception:
            return jsonify({"auth_required": True}), 401

        return f(*args, **kwargs)
    return wrapper
