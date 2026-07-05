#OVERVIEW: Login page for user to create username, join lobby, and pick an avatar
from flask import Blueprint, jsonify, request
from app.services.db_lobby_service import (generate_lobby_code, db_create_lobby)
from app.services.game_service import GameState


main_menu_bp = Blueprint('main_menu', __name__)

# Create lobby in db
@main_menu_bp.route('/db/createLobby', methods=['POST'])
def create_lobby():
    data = request.get_json()
    player_mode = data.get("player_mode")
    playlist_mode = data.get("playlist_mode")
    lobby_code = generate_lobby_code()
    print(f"Creating lobby: {lobby_code}, Playlist Mode: {playlist_mode}, Player Mode {player_mode}")
    if not lobby_code or not playlist_mode or not player_mode:
        return jsonify({"ok": False, "error": "Missing something"}), 400
    GameState.create_game(lobby_code)
    print(GameState.get_game(lobby_code).get_state())
    db_create_lobby(lobby_code=lobby_code, player_mode=player_mode, playlist_mode=playlist_mode)
    return jsonify({"ok": True,
                    "lobby_code": lobby_code,
                    "player_mode": player_mode,
                    "playlist_mode": playlist_mode
                    })

@main_menu_bp.route('/db/testGame')
def test_game():
    lobby_code = "TESTS"
    player_mode = "singleplayer"
    playlist_mode = "classic"
    GameState.create_game(lobby_code)
    print(GameState.get_game(lobby_code).get_state())
    db_create_lobby(lobby_code=lobby_code, player_mode=player_mode, playlist_mode=playlist_mode)
    return jsonify({"ok": True,
                    "lobby_code": lobby_code,
                    "player_mode": player_mode,
                    "playlist_mode": playlist_mode
                    })
