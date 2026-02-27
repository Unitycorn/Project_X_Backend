from sqlalchemy import create_engine, text
from srsly.ruamel_yaml import comments
import base64
from .id_generator import idGenerator
from flask import Flask, jsonify
import datetime
from imagekitio import ImageKit
import os
from dotenv import load_dotenv

load_dotenv()

imagekit = ImageKit(
    private_key=os.getenv('IMAGEKIT_PRIVATE_KEY'),
    base_url=os.getenv('IMAGEKIT_URL_ENDPOINT')
)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/videos/'
app.config['ALLOWED_DATATYPES'] = ('.mp4', '.mkv', '.webm')


def is_id_available(id_to_check):
    try:
        with engine.connect() as connection:
            video_ids = connection.execute(
                text("SELECT id FROM videos")
            ).fetchall()
            return id_to_check not in [row[0] for row in video_ids]
    except Exception as e:
        return {"error": str(e)}


def get_all_videos(channel_id):
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT id FROM videos WHERE videos.channel_id = :channel_id"),
                {"channel_id": channel_id}
            )
            return [row[0] for row in result.fetchall()]
    except Exception as e:
        return {"error": str(e)}


def get_user_name(user_id):
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT * FROM users WHERE users.id = :user_id"),
                {"user_id": user_id}
            )
            user = result.fetchone()
            return user.name if user else None
    except Exception as e:
        return {"error": str(e)}


def get_channel_icon(channel_id):
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT * FROM users WHERE users.id = :user_id"),
                {"user_id": channel_id}
            )
            icon = result.fetchone()
            return icon.logo_URL if icon else None
    except Exception as e:
        return {"error": str(e)}


def load_comments(video_id):
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT * FROM comments WHERE video_id = :video_id"),
                {"video_id": video_id}
            )
            comments = result.fetchall()

            return {
                index: {
                    "id": row.id,
                    "comment": row.comment,
                    "by": get_user_name(row.user_id),
                    "icon": get_channel_icon(row.user_id),
                    "channelId": row.user_id,
                    "likes": row.likes,
                    "date": row.date
                }
                for index, row in enumerate(comments)
            }
    except Exception as e:
        return {"error": str(e)}


def load_video(video_id):
    comments = load_comments(video_id)
    try:
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT * FROM videos
                JOIN users ON users.id = videos.channel_id
                WHERE videos.id = :video_id
            """), {"video_id": video_id})

            video = result.fetchone()

            return {
                "id": video_id,
                "title": video.title,
                "channelName": get_user_name(video.channel_id),
                "channelId": video.channel_id,
                "description": video.description,
                "likes": video.likes,
                "views": video.views,
                "url": app.config['UPLOAD_FOLDER'] + video_id + ".mp4",
                "comments": comments,
                "date-uploaded": video.upload_date,
                "tags": video.tags
            }
    except Exception as e:
        return {"Error": str(e)}


def add_video(file, title, description, tags, channel_id):
    upload_date = datetime.datetime.now()

    while True:
        video_id = idGenerator(8)
        if is_id_available(video_id):

            if file:
                extension = os.path.splitext(file.filename)[1]
                image_data = file.read()

                response = imagekit.files.upload(
                    file=image_data,
                    file_name=video_id + extension
                )
                print(response.url)

            with engine.connect() as connection:
                try:
                    connection.execute(text("""
                        INSERT INTO videos(id, title, description, tags, channel_id, upload_date)
                        VALUES (:video_id, :title, :description, :tags, :channel_id, :upload_date)
                    """), {
                        'video_id': video_id,
                        'title': title,
                        'description': description,
                        'tags': tags,
                        'channel_id': channel_id,
                        'upload_date': upload_date
                    })
                    connection.commit()
                    return {"Success": f"Video '{video_id}.mp4' added successfully."}
                except Exception as e:
                    return {"Error": str(e)}


def delete_comments(video_id):
    try:
        with engine.connect() as connection:
            connection.execute(
                text("DELETE FROM comments WHERE comments.video_id = :id"),
                {"id": video_id}
            )
            connection.commit()
        return None
    except Exception as e:
        return {"Error": str(e)}


def add_comment(video_id, comment, user_id, date):
    try:
        with engine.connect() as connection:
            connection.execute(text("""
                INSERT INTO comments(comment, video_id, user_id, date)
                VALUES (:comment, :video_id, :user_id, :date)
            """), {
                "video_id": video_id,
                "comment": comment,
                "user_id": user_id,
                "date": date
            })
            connection.commit()
        return {"Success": "Comment successfully added."}
    except Exception as e:
        return {"Error": str(e)}


def delete_comment(comment_id):
    try:
        with engine.connect() as connection:
            connection.execute(
                text("DELETE FROM comments WHERE comments.id = :commentId"),
                {"commentId": comment_id}
            )
            connection.commit()
        return {"Success": "Comment successfully deleted."}
    except Exception as e:
        return {"Error": str(e)}


def update_comment(comment_id, comment):
    try:
        with engine.connect() as connection:
            connection.execute(
                text("UPDATE comments SET comment = :comment WHERE comments.id = :commentId"),
                {"commentId": comment_id, "comment": comment}
            )
            connection.commit()
        return {"Success": "Comment successfully updated."}
    except Exception as e:
        return {"Error": str(e)}


def delete_video(video_id):
    delete_comments(video_id)
    try:
        with engine.connect() as connection:
            connection.execute(
                text("DELETE FROM videos WHERE videos.id = :id"),
                {"id": video_id}
            )
            connection.commit()
            return {"Success": f"Video {video_id}.mp4 deleted successfully."}
    except Exception as e:
        return {"Error": str(e)}


def update_video(video_id, title, description, tags):
    try:
        with engine.connect() as connection:
            connection.execute(text("""
                UPDATE videos
                SET title = :title,
                    description = :description,
                    tags = :tags
                WHERE videos.id = :video_id
            """), {
                'video_id': video_id,
                'title': title,
                'description': description,
                'tags': tags
            })
            connection.commit()
            return {"Success": "Video successfully updated."}
    except Exception as e:
        return {"Error": str(e)}
