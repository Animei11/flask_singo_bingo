import os
from flask import Flask
from app.config import Config
from app.extensions import db, migrate
# from flask_socketio import SocketIO

# socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

    # Register models
    from app import models
    # Register blueprints
    from app.routes.music_player_routes import music_player_routes_bp
    app.register_blueprint(music_player_routes_bp)

    from app.routes.player_routes import player_routes_bp
    app.register_blueprint(player_routes_bp)

    from app.blueprints.main_menu import main_menu_bp
    app.register_blueprint(main_menu_bp)

    from app.blueprints.login import login_bp
    app.register_blueprint(login_bp)

    from app.blueprints.lobby import lobby_bp
    app.register_blueprint(lobby_bp)

    from app.music_player.spotify.oauth import spotify_oauth_bp
    app.register_blueprint(spotify_oauth_bp)

    from app.blueprints.spotify import spotify_bp
    app.register_blueprint(spotify_bp)



    # Attach Socket.IO (no sockets running yet)
    # socketio.init_app(app)

    # Import socket handlers AFTER init
    # from app.blueprints import socket_connector

    return app
