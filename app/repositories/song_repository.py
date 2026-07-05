# Overview: All direct database access for the Song model. No business rules here.
from psycopg2.extras import execute_values
from sqlalchemy import text
from app.extensions import db


def add_all_if_missing(playlist_details, playlist_id):
    """ Adding songs to song db if it does not exist already """
    # Check if playlist already exists
    result = db.session.execute(
        text("SELECT 1 FROM songs WHERE playlist_id = :playlist_id LIMIT 1;"),
        {"playlist_id": playlist_id}
        ).fetchone()

    if result is None:
        conn = db.session.connection().connection
        with conn.cursor() as cur:
            data_to_insert = [(uri, name, playlist_id) for (uri, name) in playlist_details]
            query = """
                INSERT INTO songs (song_uri, song_name, playlist_id)
                VALUES %s;
            """
            execute_values(cur, query, data_to_insert)
        conn.commit()
    else:
        print("Songs already exist for this playlist.")


def get_for_lobby(lobby_code):
    """ Returns the songs belonging to the playlist attached to this lobby """
    result = db.session.execute(
        text("""
             SELECT song_name, song_uri FROM lobbies
             join songs on lobbies.playlist_id = songs.playlist_id
             where lobby_code = :lobby_code;"""),
        {"lobby_code": lobby_code}
        ).fetchall()
    if result is None:
        print("Error retrieving songs for bingo")
    result = [dict(song_name=row.song_name, song_uri=row.song_uri) for row in result]
    return result
