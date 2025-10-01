from sqlalchemy import create_engine, text
from .id_generator import idGenerator
from .data_manager import get_all_videos, delete_video, delete_comments, load_video
from flask import jsonify
import datetime

# Define the database URL
DB_URL = "sqlite:///./Project_X_Backend/data/database.sqlite"

# Create the engine
engine = create_engine(DB_URL, echo=False)


def is_id_available(id_to_check):
    try:
        with engine.connect() as connection:
            video_ids = connection.execute(text("SELECT id FROM users")).fetchall()
            if id_to_check in video_ids:
                return False
            else:
                return True
    except Exception as e:
        return {"error": str(e)}


def add_channel(name, description, login, password):
    """Adds a new entry in the channels table"""
    channel_id = idGenerator(8)
    if is_id_available(channel_id):
        logo_url = idGenerator(18)
        with engine.connect() as connection:
            try:
                connection.execute(text("""INSERT INTO users(id, name, about, logo_URL, login_name, password)
                                           VALUES (:channel_id, :name, :description, :logo_URL, :login, :password)"""),
                                 {"channel_id": channel_id, "name": name, "description": description,
                                            "logo_URL": logo_url + ".jpg", "login": login, "password": password})
                connection.commit()
                return {"Success": f"Channel {channel_id}  has been successfully created"}
            except Exception as e:
                return {f"Error: {e}"}


def remove_channel(channel_id):
    """Deletes a channel and all its videos with comments from the database."""
    all_videos = get_all_videos(channel_id)
    for video_id in all_videos:
        delete_comments(video_id)
        delete_video(video_id)

    with engine.connect() as connection:
        try:
            connection.execute(text("DELETE FROM users WHERE users.id = :id"),
                                {"id": channel_id})
            connection.commit()
            return {"400": f"Channel {channel_id}  has been successfully deleted"}
        except Exception as e:
            return {f"Error: {e}"}


def get_channel(channel_id):
    """Returns channel data and associated videos for the given channel id"""
    all_videos = get_all_videos(channel_id)
    videos = {}
    index = 0
    for video_id in all_videos:
        videos[index] = load_video(video_id)
        index += 1
    with engine.connect() as connection:
        try:
            result = connection.execute(text("SELECT * FROM users WHERE users.id = :id"),
                                {"id": channel_id})
            channel = result.fetchone()
            return {"name": channel.name, "abonnements": channel.abonnements, "about": channel.about,
                    "playlists": channel.playlists, "logo URL": channel.logo_URL, "videos": videos}
        except Exception as e:
            return {f"Error: {e}"}


def edit_channel(channel_id, channel_name, about, login, password):
    """Updates the channel data for the given channel id in the users table"""
    with engine.connect() as connection:
        try:
            connection.execute(text("""UPDATE users
                                         SET 'name' = :channel_name, 'about'= :about, 'login_name'= :login, 'password'= :password
                                         WHERE users.id == :channel_id"""),
                                {'channel_id': channel_id, 'channel_name': channel_name, 'about': about, 'login': login, 'password': password})
            connection.commit()
            return {"Success": "Channel infos have been successfully updated."}
        except Exception as e:
            return {f"Error": str(e)}
