from flask import Blueprint, jsonify, request
from app.services.db_lobby_service import ( 
    db_get_all_active_lobbies
)
from app.services.db_player_service import ( 
    db_get_player_avatar
)


lobby_bp = Blueprint('lobby', __name__)

# Retrieves all active lobby codes
@lobby_bp.route('/db/getLobbyCode')
def get_lobby_code():
    list_of_lobbies = db_get_all_active_lobbies()
    print(list_of_lobbies)
    return jsonify(list_of_lobbies)

@lobby_bp.route('/db/getPlayerAvatar')
def get_player_avatar():
    username = request.args.get("username")
    print(f"Received request for player avatar with username: {username}")
    if not username:
        return jsonify({"ok": False, "error": "Missing username"}), 400
    avatar = db_get_player_avatar(username)
    if avatar:
        return jsonify({"ok": True, "avatar_file_name": avatar.avatar_file_name})
    else:
        return jsonify({"ok": False, "error": "Player or avatar not found"}), 404