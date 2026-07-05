# OVERVIEW: Routes for players
from flask import Blueprint, render_template, request, jsonify, session, url_for, redirect
from app.services.db_lobby_service import db_get_lobby

player_routes_bp = Blueprint("player_routes", __name__)
@player_routes_bp.route('/')
@player_routes_bp.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

# Render bingo card
@player_routes_bp.route('/bingoCard/<lobby_code>')
def generate_bingo_card(lobby_code):
    username = session.get("username")
    session_lobby = session.get("lobby_code")
    if not username or session_lobby != lobby_code:
        return redirect(url_for("player_routes.login"))
    return render_template(
        "bingoCard.html",
        lobbyCode=lobby_code,
        username=username
    )
