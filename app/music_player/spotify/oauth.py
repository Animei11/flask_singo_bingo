# OVERVIEW: Spotify OAuth setup
import os
from flask import Blueprint, redirect, session, request
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

spotify_oauth_bp = Blueprint('spotify_oauth', __name__)
load_dotenv()

# Step 1: Set up Spotify configurations
spotify_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    scope="playlist-read-private user-read-playback-state user-modify-playback-state",
)
# Step 2: Redirect user to Spotify for authentication
@spotify_oauth_bp.route("/spotify/login")
def spotify_login():
    auth_url = spotify_oauth.get_authorize_url()
    return redirect(auth_url)

# Step 3: Creates access token after Spotify redirects back
@spotify_oauth_bp.route("/callback")
def spotify_callback():
    code = request.args.get("code")
    token_info = spotify_oauth.get_access_token(code)
    session["spotify_token"] = token_info
    return redirect("/")


class SpotifyNotAuthenticated(Exception):
    pass

# Step 4: Return token 
def get_spotify_client(token_info):
    if not token_info:
        return None

    if spotify_oauth.is_token_expired(token_info):
        token_info = spotify_oauth.refresh_access_token(
            token_info["refresh_token"]
        )
        session["spotify_token"] = token_info

    return Spotify(auth=token_info["access_token"])