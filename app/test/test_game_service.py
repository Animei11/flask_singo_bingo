"""
Unit tests for GameState (app/services/game_service.py).

These are "unit" tests: each one exercises GameState in isolation, with
its one real dependency (Redis) swapped for the `fake_redis` fixture from
conftest.py. No real Redis server, no network, nothing left over between
test runs. That's what makes them fast enough to run on every save and
deterministic enough to trust when they fail.
"""
import pytest

from app.services.game_service import GameState

LOBBY_CODE = "TESTS"


def test_create_game_sets_initial_state(fake_redis):
    GameState.create_game(LOBBY_CODE)

    state = GameState.get_game(LOBBY_CODE).get_state()

    assert state["status"] == "waiting"
    assert state["players"] == []
    assert state["playlist"] == []


def test_create_game_twice_raises(fake_redis):
    GameState.create_game(LOBBY_CODE)

    with pytest.raises(ValueError):
        GameState.create_game(LOBBY_CODE)


def test_get_game_for_unknown_lobby_raises(fake_redis):
    with pytest.raises(ValueError):
        GameState.get_game("NOPE")


def test_add_player_appends_username(fake_redis):
    GameState.create_game(LOBBY_CODE)
    game = GameState.get_game(LOBBY_CODE)

    game.add_player("alice")

    assert game.get_state()["players"] == ["alice"]


def test_add_player_marks_lobby_active_once_full(fake_redis):
    GameState.create_game(LOBBY_CODE)
    game = GameState.get_game(LOBBY_CODE)

    for i in range(8):
        game.add_player(f"player{i}")

    assert game.get_state()["status"] == "active"


def test_add_player_rejects_a_ninth_player(fake_redis):
    GameState.create_game(LOBBY_CODE)
    game = GameState.get_game(LOBBY_CODE)
    for i in range(8):
        game.add_player(f"player{i}")

    with pytest.raises(ValueError):
        game.add_player("one_too_many")


@pytest.fixture
def game_with_bingo_card(fake_redis):
    """A game with one player who has a 5x5 card, laid out row by row.

    card[0:5] is row 0, card[5:10] is row 1, and so on -- that layout is
    what lets the tests below mark "a row" or "a column" just by picking
    the right slice of `card`.
    """
    GameState.create_game(LOBBY_CODE)
    game = GameState.get_game(LOBBY_CODE)
    card = [f"song-{i}" for i in range(25)]
    game.add_bingo_player("alice", card)
    return game, card


def test_marking_a_full_row_is_a_bingo(game_with_bingo_card):
    game, card = game_with_bingo_card

    for song_name in card[0:5]:  # row 0
        game.mark_tile("alice", song_name)

    assert game.check_bingo("alice") is True


def test_marking_a_full_column_is_a_bingo(game_with_bingo_card):
    game, card = game_with_bingo_card

    for song_name in card[0:25:5]:  # column 0: indices 0, 5, 10, 15, 20
        game.mark_tile("alice", song_name)

    assert game.check_bingo("alice") is True


def test_marking_a_partial_row_is_not_a_bingo(game_with_bingo_card):
    game, card = game_with_bingo_card

    for song_name in card[0:4]:  # only 4 of the 5 tiles in row 0
        game.mark_tile("alice", song_name)

    assert game.check_bingo("alice") is False


def test_free_space_marks_the_center_tile(game_with_bingo_card):
    game, _ = game_with_bingo_card

    game.mark_tile("alice", "FREE SPACE")

    marked_tiles = game.get_player_state("alice")["marked_tiles"]
    # Redis only stores JSON, and JSON has no tuple type -- the (2, 2)
    # tuple that mark_tile builds in memory comes back out as the list
    # [2, 2] once it's round-tripped through fake_redis. That's not a
    # fake_redis quirk, real Redis behaves identically, since
    # game_service.py does the json.dumps/json.loads itself.
    assert [2, 2] in marked_tiles


def test_playlist_tracks_current_and_advances_to_next_song(fake_redis):
    GameState.create_game(LOBBY_CODE)
    game = GameState.get_game(LOBBY_CODE)
    songs = [
        {"song_name": "Song A", "song_uri": "uri-a"},
        {"song_name": "Song B", "song_uri": "uri-b"},
    ]

    game.set_playlist(songs)
    assert game.get_current_song() == "Song A"

    next_song = game.get_next_song()
    assert next_song["song_name"] == "Song B"
    assert game.get_current_song() == "Song B"

    # We're at the last song now -- there's nothing after it.
    assert game.get_next_song() is None
