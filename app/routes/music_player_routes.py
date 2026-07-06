# OVERVIEW: Routes for music player
from flask import Blueprint, render_template
from app.services import lobby_service
from app.services.game_service import GameState


music_player_routes_bp = Blueprint("music_player_routes", __name__)

# Testing page
@music_player_routes_bp.route('/testPage')
def test_page():
    return render_template('testPage.html')

## COMPUTER ROUTES ##
# Main Menu - Starting point for computer
@music_player_routes_bp.route('/mainMenu')
def main_menu():
    return render_template('mainMenu.html')

# Sends players to route with lobby associated with their lobby code
@music_player_routes_bp.route('/lobby/<lobby_code>')
def lobby(lobby_code):
    lobby_exists = lobby_service.get_lobby(lobby_code)
    print(lobby_exists)
    if not lobby_exists:
        return "Lobby not found", 404
    print(GameState.get_game(lobby_code).get_state())
    return render_template('lobby.html', lobbyCode=lobby_code)

# Starts playing music
@music_player_routes_bp.route("/startGame/<lobby_code>")
def start_game(lobby_code):
    lobby_exists = lobby_service.get_lobby(lobby_code)
    print(lobby_exists)
    if not lobby_exists:
        return "Lobby not found", 404
    return render_template("startGame.html", lobbyCode=lobby_code)

# Game Over Bro
@music_player_routes_bp.route("/gameOver/<lobby_code>")
def game_over(lobby_code):
    lobby_exists = lobby_service.get_lobby(lobby_code)
    print(lobby_exists)
    if not lobby_exists:
        return "Lobby not found", 404
    return render_template("gameOver.html", lobbyCode=lobby_code)
