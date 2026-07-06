"""
OVERVIEW: GameState: Used to store information needed between frontend and backend (so not all details)
Includes: Lobby code, lobby status (if players can join or not), players' username, 
          playlist, index of current song, name of current song
"""

import json
from app.extensions import redis_client

class GameState:
    def __init__(self, lobby_code: str):
        self.lobby_code = lobby_code

    # ---------------------------------------
    # General GameState - Setters and Getters 
    # ---------------------------------------
    def get_state(self):
        """Return the current state as a dictionary."""
        state_str = redis_client.get(f"game:{self.lobby_code}")
        if not state_str:
            raise ValueError("Game not found")
        state = json.loads(state_str)
        state["lobby_code"] = self.lobby_code  # Add lobby_code to the state
        return state


    # ---------------------------
    # Lobby - Setters and Getters 
    # ---------------------------
    def set_lobby_status(self, status: str):
        """Set the lobby status (waiting: players can join (default)
                                 active: game has started, no more players can join, or max players have joined
                                 inactive: game has ended)
        """
        state = self.get_state()
        state["status"] = status
        redis_client.set(f"game:{self.lobby_code}", json.dumps(state))


    # -----------------------------
    # Players - Setters and Getters 
    # -----------------------------
    def add_player(self, username: str):
        """Add a player to the game."""
        state = self.get_state()
        if len(state["players"]) == 8:
            raise ValueError("Lobby is full")
        elif username not in state["players"]:
            state["players"].append(username)
            if len(state["players"]) == 8:
                state["status"] = "active"
            redis_client.set(f"game:{self.lobby_code}", json.dumps(state))


    # -----------------------------
    # Players - Bingo-specific
    # -----------------------------
    def add_bingo_player(self, username: str, bingo_card: list):
        """Add a player with a bingo card."""
        state = self.get_state()
        if "bingo_players" not in state:
            state["bingo_players"] = {}

        if username not in state["bingo_players"] or state["bingo_players"][username]["bingo_card"] == []:
            state["bingo_players"][username] = {
                "bingo_card": bingo_card,  # 5x5 list
                "marked_tiles": [],  # List of marked tile positions (i, j)
                "has_bingo": False
            }
            redis_client.set(f"game:{self.lobby_code}", json.dumps(state))
        print(f"Added bingo player {username} with card {bingo_card} to game {self.lobby_code}")
    
    def reset_bingo_players(self):
        """Reset bingo players for a new game."""
        state = self.get_state()
        state["bingo_players"] = {}
        redis_client.set(f"game:{self.lobby_code}", json.dumps(state))

    def mark_tile(self, username: str, song_name: str):
        """Mark a tile for a player."""
        state = self.get_state()
        player = state.get("bingo_players", {}).get(username)
        if not player:
            raise ValueError("Player not found")
        # TODO: Fix tile pos, always returns None
        if song_name == "FREE SPACE":
            tile_pos = (2, 2) 
        else:
            print(f"Songs: {player['bingo_card']}")
            for i in range(25):
                row = i // 5
                col = i % 5
                if player["bingo_card"][i] == song_name:
                    tile_pos = (row, col)
                    break

        if tile_pos not in player["marked_tiles"]:
            player["marked_tiles"].append(tile_pos)
            redis_client.set(f"game:{self.lobby_code}", json.dumps(state))
        print(f"Marked tile {tile_pos} for player {username} in game {self.lobby_code}")

    def check_bingo(self, username: str):
        """Check if a player has bingo."""
        state = self.get_state()
        player = state.get("bingo_players", {}).get(username)
        if not player:
            raise ValueError("Player not found")
        print(f"Checking bingo for player {username} with marked tiles {player['marked_tiles']} in game {self.lobby_code}")
        marked = { (r, c) for r, c in player['marked_tiles'] }
        lines = []
        # Rows
        for r in range(5):
            lines.append([(r, c) for c in range(5)])
        # Columns
        for c in range(5):
            lines.append([(r, c) for r in range(5)])
        # Diagonals
        lines.append([(i, i) for i in range(5)])
        lines.append([(i, 4 - i) for i in range(5)])
        return any(all(coord in marked for coord in line) for line in lines)

    def set_winner(self, username: str):
        """Set the winner of the bingo game."""
        state = self.get_state()
        state["winner"] = username
        if username in state.get("bingo_players", {}):
            state["bingo_players"][username]["has_bingo"] = True
        redis_client.set(f"game:{self.lobby_code}", json.dumps(state))

    def get_player_state(self, username: str):
        """Return the bingo-specific state for a player."""
        state = self.get_state()
        existing_player = state.get("bingo_players", {}).get(username)
        return existing_player if existing_player else None
    
    # ------------------------------------
    # Playlist/Songs - Setters and Getters 
    # ------------------------------------
    def set_playlist_id(self, playlist_id):
        """ Set playlist id"""
        state = self.get_state()
        state["playlist_id"] = playlist_id
        redis_client.set(f"game:{self.lobby_code}", json.dumps(state))

    def set_playlist(self, songs: list):
        """Set the playlist for this game and start from the first song."""
        state = self.get_state()
        print(songs)
        state["playlist"] = songs
        state["index"] = 0
        state["current_song"] = songs[0] if songs else None
        redis_client.set(f"game:{self.lobby_code}", json.dumps(state))

    def get_playlist(self):
        state = self.get_state()
        return state["playlist"]

    def get_next_song(self):
        """Return the next song in the playlist, or None if at the end."""
        state = self.get_state()
        next_index = state["index"] + 1
        if next_index < len(state["playlist"]):
            state["index"] = next_index
            state["current_song"] = state["playlist"][next_index]
            redis_client.set(f"game:{self.lobby_code}", json.dumps(state))
            return state["current_song"]
        return None
    
    def get_current_song(self):
        state = self.get_state()
        current_song = state["current_song"]["song_name"] if state["current_song"] else None
        return current_song
    
    # ----------
    # Resetters
    # ----------
    def reset_playlist(self):
        state = self.get_state()
        state["playlist_id"] = None
        state["playlist"] = []
        state["index"] = 0
        state["current_song"] = None
        redis_client.set(f"game:{self.lobby_code}", json.dumps(state))
    
    def delete_game(self):
        if not redis_client.exists(f"game:{self.lobby_code}"):
            raise ValueError("Game does not exist")

        redis_client.delete(f"game:{self.lobby_code}")
        print("Game deleted successfully")
        return "Game deleted successfully"

    # -------------
    # Class Methods
    # -------------
    @classmethod
    def get_game(cls, lobby_code: str):
        """Return the GameState instance for a lobby code."""
        state_str = redis_client.get(f"game:{lobby_code}")
        if not state_str:
            raise ValueError("Game not found")
        return cls(lobby_code)  # Return instance, but state is in Redis

    @classmethod
    def create_game(cls, lobby_code: str):
        if redis_client.exists(f"game:{lobby_code}"):
            raise ValueError("Game already exists")

        initial_state = {
            "status": "waiting",
            "players": [],
            "playlist_id": None,
            "playlist": [],
            "index": 0,
            "current_song": None
        }

        redis_client.set(f"game:{lobby_code}", json.dumps(initial_state))

        return cls(lobby_code) 