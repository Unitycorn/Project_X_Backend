import json
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from .id_generator import idGenerator
from .data_manager import get_all_videos, delete_video, delete_comments, load_video
from flask import jsonify, Flask
import datetime
import getpass
import hashlib
from cryptography.fernet import Fernet

load_dotenv(verbose=True)

# Define the database URL
DB_URL = os.getenv('DB_URL')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads/images/'
app.config['ALLOWED_DATATYPES'] = '.jpg', '.jpeg', '.webp'

# Create the engine
engine = create_engine(DB_URL, echo=False)
print("DB URL: " + str(engine.url))
cipher_suite = Fernet(os.getenv('FERNET_KEY'))
print(cipher_suite)


def login(login_name, password):
    try:
        with engine.connect() as connection:
            print("submitted password: " + str(password))
            encrypted_password = cipher_suite._encrypt_from_parts(password.encode(), 0,b'\xbd\xc0,\x16\x87\xd7G\xb5\xe5\xcc\xdb\xf9\x07\xaf\xa0\xfa')
            print("encrypted password: " + str(encrypted_password))
            channel = connection.execute(text("SELECT * FROM users WHERE login_name = :login_name AND password = :password"),
                                      {"login_name": login_name, "password": encrypted_password}).fetchone()
            if channel is None:
                return jsonify({"error": "Login name or password incorrect"}), 401
            else:
                return {"user":{"name": channel.name, "id": channel.id, "email": channel.login_name,
                     "icon": channel.logo_URL},
                "token": "Example token"}
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def name_is_available(name):
    try:
        with engine.connect() as connection:
            channel_names = connection.execute(text("SELECT name FROM users")).fetchall()
            for channel_name in channel_names:
                if name == channel_name[0]:
                    return False
            return True
    except Exception as e:
        return {"error": str(e)}


def is_already_registered(login_handle):
    print("Check if name is already registered:" + login_handle)
    try:
        with engine.connect() as connection:
            print("Check if name is already registered in try:" + login_handle)
            login_names = connection.execute(text("SELECT login_name FROM users")).fetchall()
            for login_name in login_names:
                if login_handle == login_name[0]:
                    print("check match" + login_name[0] + login_handle)
                    return True
            return False
    except Exception as e:
        return {"error": str(e)}


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


def add_channel(file, name, description, login_name, password):
    """Adds a new entry in the channels table if the login is not already in use"""

    if not is_already_registered(login_name) and name_is_available(name):

        while True:
            print("submitted password: " + str(password))
            channel_id = idGenerator(8)
            logo = ""
            if is_id_available(channel_id):
                if file:
                    extension = os.path.splitext(file.filename)[1]
                    logo_url = idGenerator(18)
                    logo = logo_url + extension
                    file.save(os.path.join(
                        app.config['UPLOAD_FOLDER'],
                        logo
                    ))

                encrypted_password = cipher_suite._encrypt_from_parts(password.encode(), 0,b'\xbd\xc0,\x16\x87\xd7G\xb5\xe5\xcc\xdb\xf9\x07\xaf\xa0\xfa')

                with engine.connect() as connection:
                    try:
                        connection.execute(text("""INSERT INTO users(id, name, about, logo_URL, login_name, password)
                                                   VALUES (:channel_id, :name, :description, :logo_URL, :login, :password)"""),
                                            {"channel_id": channel_id, "name": name, "description": description,
                                            "logo_URL": logo, "login": login_name, "password": encrypted_password})
                        connection.commit()
                        return {"Success": f"Channel {channel_id}  has been successfully created"}

                    except Exception as e:
                        return {f"Error: {e}"}
    else:
        return {"Error": f"{login_name} is already registered"}


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
            return {f"Error": str(e)}


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
            # encrypted_password = channel.password
            # print(cipher_suite.decrypt(encrypted_password.encode()).decode())
            return {"name": channel.name, "abonnements": channel.abonnements, "about": channel.about,
                    "playlists": channel.playlists, "logo URL": channel.logo_URL, "videos": videos}
        except Exception as e:
            return {f"Error": str(e)}


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
