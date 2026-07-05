#OVERVIEW: All spotiPy related functions
import random
from flask import (
    Blueprint, 
    jsonify, 
    request,
    g
) 
from app.services import lobby_service, playlist_service
from app.services.game_service import GameState
from app.music_player.spotify.decorator import require_spotify


spotify_bp = Blueprint('spotify', __name__)

# Fetch playlists from Spotify and add songs to DB
# Sends 4 playlists to front end for user to select playlist
@spotify_bp.route('/spotify/getplaylists')
def spotify_get_playlists():
    # TODO: Create wheel to display later
    mode = request.args.get("mode")
    list_of_playlists = playlist_service.get_playlists(playlist_mode=mode)
    return jsonify(list_of_playlists)


# Get selected playlist from user, save to db, return list of songs
@spotify_bp.route('/spotify/playlists/selectedPlaylist', methods=['POST'])
@require_spotify
def spotify_get_selected_playlist():
    data = request.get_json()
    playlist_id = data.get("playlist_id")
    playlist_uri = data.get("playlist_uri")
    playlist_name = data.get("playlist_name")
    lobby_code = data.get("lobby_code")
    if not playlist_id or not playlist_uri or not playlist_name or not lobby_code:
        return jsonify({"ok": False, "error": "Missing something"}), 400
    game = GameState.get_game(lobby_code=lobby_code)
    game.reset_bingo_players()  # Reset all players' bingo cards when a new playlist is selected
    game.reset_playlist()
    game.set_playlist_id(playlist_id)
    lobby_service.add_playlist_to_lobby(lobby_code=lobby_code, playlist_id=playlist_id)
    playlist_details = g.music_provider.get_playlist_details(playlist_id=playlist_id, playlist_uri=playlist_uri)
    playlist_service.add_all_songs(playlist_details, playlist_id)
    return jsonify({"ok": True})  


# Returns a randomized playlist of 24 songs to front end
@spotify_bp.route('/spotify/playlists/getPlayersSongs', methods=['GET'])
def spotify_get_playlist_songs():
    lobby_code = request.args.get("lobby_code")
    username = request.args.get("username")
    if not lobby_code or not username:
        return jsonify({"ok": False, "error": "Missing lobby_code or username"}), 400
    game = GameState.get_game(lobby_code=lobby_code)
    existing_player = game.get_player_state(username)
    # TODO: Return JSON of marked tiles for this player to front end to update bingo card state on page refresh
    if existing_player and existing_player["bingo_card"]:
        return jsonify({
            "ok": True,
            "songs": existing_player["bingo_card"],
            "marked_tiles": existing_player["marked_tiles"]
    })
    playlist = game.get_playlist()
    if playlist:
        songs = playlist 
    else:
        songs = playlist_service.get_songs_for_bingo_card(lobby_code)
        game.set_playlist(songs)
    random.shuffle(songs)
    songs = [song["song_name"] for song in songs]
    songs = songs[:24]
    songs.insert(12, "FREE SPACE")
    game.add_bingo_player(username, songs)
    return jsonify({
        "ok": True,
        "songs": songs
    })   
 
@spotify_bp.route('/spotify/playlists/getMasterPlaylist', methods=['GET'])
def spotify_get_master_playlist():
    lobby_code = request.args.get("lobby_code")
    if not lobby_code:
        return jsonify({"ok": False, "error": "Missing lobby_code"}), 400
    game = GameState.get_game(lobby_code=lobby_code)
    playlist = game.get_playlist()
    if playlist:
        songs = playlist 
    else:
        songs = playlist_service.get_songs_for_bingo_card(lobby_code)
        random.shuffle(songs)
        game.set_playlist(songs)
    return jsonify({
        "ok": True,
        "songs": songs
    })


# TODO: Start playing from the most popular parts of the song
@spotify_bp.route('/spotify/playlists/playsong', methods=['GET'])
@require_spotify
def play_song():
    song_uri = request.args.get("song_uri")
    if not song_uri:
        return jsonify({"ok": False, "error": "Missing song_uri"}), 400
    g.music_provider.play_song(song_uri)
    return jsonify({"ok": True})

@spotify_bp.route('/spotify/playlists/stopsong')
@require_spotify
def stop_song():
    g.music_provider.stop_song()
    return jsonify({"ok": True})

@spotify_bp.route('/spotify/playlists/nextIndex')
@require_spotify
def next_index():
    lobby_code = request.args.get("lobby_code")
    if not lobby_code:
        return jsonify({"ok": False, "error": "Missing lobby_code"}), 400
    game = GameState.get_game(lobby_code=lobby_code)
    next_song = game.get_next_song()
    if not next_song:
        return jsonify({"ok": False, "error": "No more songs in playlist"}), 400
    return jsonify({"ok": True, "next_song": next_song})

@spotify_bp.route('/spotify/playlists/pausesong')
@require_spotify
def pause_song():
    # g.music_provider.pause_song()
    return jsonify({"ok": True})


#  USE THIS ROUTE FOR TESTING 
@spotify_bp.route('/spotify/playlists/verifySong')
def verify_song_clicked():
    lobby_code = request.args.get("lobby_code")
    selected_song = request.args.get("song_title")
    username = request.args.get("username")
    print(f"Received request to verify song: {selected_song} for lobby: {lobby_code} and user: {username}")
    game = GameState.get_game(lobby_code=lobby_code)
    correct_song = game.get_current_song()
    print(f"Current song from game state: {correct_song}")
    if correct_song == selected_song or selected_song == "FREE SPACE":
        print("Song verified successfully!")
        game.mark_tile(username, selected_song)
        player_state = game.get_player_state(username)
        if len(player_state["marked_tiles"]) >= 5:
            has_bingo = game.check_bingo(username)
            if has_bingo:
                game.set_winner(username)
                return jsonify({"ok": True, "hasBingo": True})
        return jsonify({"ok": True})
    else:
        print("Song verification failed.")
        return jsonify({"ok": False, "error": "Incorrect song"})