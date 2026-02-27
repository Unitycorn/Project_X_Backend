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
from data_models.models import db

load_dotenv(verbose=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads/images/'
app.config['ALLOWED_DATATYPES'] = ('.jpg', '.jpeg', '.webp')


#print("DB URL: " + str(engine.url))

cipher_suite = Fernet(os.getenv('FERNET_KEY'))
print(cipher_suite)


def login(login_name, password):
    try:
        with db.engine.connect() as connection:
            encrypted_password = cipher_suite._encrypt_from_parts(
                password.encode(),
                0,
                b'\xbd\xc0,\x16\x87\xd7G\xb5\xe5\xcc\xdb\xf9\x07\xaf\xa0\xfa'
            )

            channel = connection.execute(
                text("SELECT * FROM users WHERE login_name = :login_name AND password = :password"),
                {"login_name": login_name, "password": encrypted_password}
            ).fetchone()

            if channel is None:
                return {"error": "Login name or password incorrect"}

            return {
                "user": {
                    "name": channel.name,
                    "id": channel.id,
                    "email": channel.login_name,
                    "icon": channel.logo_URL
                },
                "token": "Example token"
            }

    except Exception as e:
        return {"error": str(e)}


def name_is_available(name):
    try:
        with db.engine.connect() as connection:
            channel_names = connection.execute(
                text("SELECT name FROM users")
            ).fetchall()

            return name not in [row[0] for row in channel_names]

    except Exception as e:
        return {"error": str(e)}


def is_already_registered(login_handle):
    try:
        with db.engine.connect() as connection:
            login_names = connection.execute(
                text("SELECT login_name FROM users")
            ).fetchall()

            return login_handle in [row[0] for row in login_names]

    except Exception as e:
        raise Exception(f"Database connection error: {str(e)}")


def is_id_available(id_to_check):
    try:
        with db.engine.connect() as connection:
            user_ids = connection.execute(
                text("SELECT id FROM users")
            ).fetchall()

            return id_to_check not in [row[0] for row in user_ids]

    except Exception as e:
        return {"error": str(e)}


def add_channel(file, name, description, login_name, password):
    try:
        if not is_already_registered(login_name) and name_is_available(name):

            while True:
                channel_id = idGenerator(8)
                logo = ""

                if is_id_available(channel_id):

                    if file:
                        extension = os.path.splitext(file.filename)[1]
                        logo_url = idGenerator(18)
                        logo = logo_url + extension
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], logo))

                    encrypted_password = cipher_suite._encrypt_from_parts(
                        password.encode(),
                        0,
                        b'\xbd\xc0,\x16\x87\xd7G\xb5\xe5\xcc\xdb\xf9\x07\xaf\xa0\xfa'
                    )

                    with db.engine.connect() as connection:
                        connection.execute(text("""
                            INSERT INTO users(id, name, about, logo_URL, login_name, password)
                            VALUES (:channel_id, :name, :description, :logo_URL, :login, :password)
                        """), {
                            "channel_id": channel_id,
                            "name": name,
                            "description": description,
                            "logo_URL": logo,
                            "login": login_name,
                            "password": encrypted_password
                        })

                        connection.commit()

                        return {"Success": f"Channel {channel_id} has been successfully created"}

        if is_already_registered(login_name):
            return {"error": f"{login_name} is already registered"}

        return {"error": f"{name} is already in use"}

    except Exception as e:
        return {"error": f"Database connection error: {str(e)}"}


def remove_channel(channel_id):
    all_videos = get_all_videos(channel_id)

    for video_id in all_videos:
        delete_comments(video_id)
        delete_video(video_id)

    try:
        with db.engine.connect() as connection:
            connection.execute(
                text("DELETE FROM users WHERE users.id = :id"),
                {"id": channel_id}
            )
            connection.commit()

        return {"Success": f"Channel {channel_id} has been successfully deleted"}

    except Exception as e:
        return {"Error": str(e)}


def get_channel(channel_id):
    all_videos = get_all_videos(channel_id)
    videos = {index: load_video(video_id) for index, video_id in enumerate(all_videos)}

    try:
        with db.engine.connect() as connection:
            result = connection.execute(
                text("SELECT * FROM users WHERE users.id = :id"),
                {"id": channel_id}
            )

            channel = result.fetchone()

            return {
                "name": channel.name,
                "abonnements": channel.abonnements,
                "about": channel.about,
                "playlists": channel.playlists,
                "logo URL": channel.logo_URL,
                "videos": videos
            }

    except Exception as e:
        return {"Error": str(e)}


def edit_channel(channel_id, channel_name, about, login, password):
    try:
        with db.engine.connect() as connection:
            connection.execute(text("""
                UPDATE users
                SET name = :channel_name,
                    about = :about,
                    login_name = :login,
                    password = :password
                WHERE users.id = :channel_id
            """), {
                'channel_id': channel_id,
                'channel_name': channel_name,
                'about': about,
                'login': login,
                'password': password
            })

            connection.commit()

        return {"Success": "Channel infos have been successfully updated."}

    except Exception as e:
        return {"Error": str(e)}
