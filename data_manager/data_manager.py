from sqlalchemy import create_engine, text
from srsly.ruamel_yaml import comments
from .id_generator import idGenerator
from flask import Flask, jsonify
import datetime
import os
from dotenv import load_dotenv

load_dotenv(verbose=True)
# Define the database URL
DB_URL = os.getenv('DB_URL')

# Create the engine
engine = create_engine(DB_URL, echo=False)
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads/'
app.config['ALLOWED_DATATYPES'] = '.mp4', '.mkv', '.webm'


def is_id_available(id_to_check):
    try:
        with engine.connect() as connection:
            video_ids = connection.execute(text("SELECT id FROM videos")).fetchall()
            if id_to_check in video_ids:
                return False
            else:
                return True
    except Exception as e:
        return {"error": str(e)}


def get_all_videos(channel_id):
    """Returns a list of all video ids in the channel"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("""SELECT id FROM videos WHERE videos.channel_id = :channel_id"""),
                                         {"channel_id": channel_id})
            videos = result.fetchall()
            video_list = []
            for row in videos:
                video_list.append(row[0])
            return video_list
    except Exception as e:
        return {"error": str(e)}


def get_user_name(user_id):
    """Loads the name of the channel for the given id"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("""SELECT * FROM users WHERE users.id = :user_id"""),
                                         {"user_id": user_id})
            user = result.fetchone()
            return user.name
    except Exception as e:
        return {"error": str(e)}


def load_comments(video_id):
    """Retrieves comments associated with the specified video"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("""SELECT *
                                                  FROM comments
                                                  JOIN videos ON videos.id = comments.video_id
                                                  WHERE videos.id = :video_id"""),
                                         {"video_id": video_id})
            comments = result.fetchall()
            return {comments.index(row): {"comment": row[1], "by": get_user_name(row.user_id), "likes": row.likes} for row in comments}
    except Exception as e:
        return {"error": str(e)}


def load_video(video_id):
    """Retrieve video and comments with video id from the database."""
    comments = load_comments(video_id)
    with engine.connect() as connection:
        try:
            result = connection.execute(text("""SELECT * FROM videos
                                         JOIN users ON users.id = videos.channel_id WHERE videos.id = :video_id"""),
                                            {"video_id": video_id})
            video = result.fetchone()
            return {"title": video.title, "channel": get_user_name(video.id), "description": video.description,
                "likes": video.likes, "views": video.views, "url": app.config['UPLOAD_FOLDER'] + video_id + ".mp4",
                "comments": comments, "date-uploaded": video.upload_date}
        except Exception as e:
            return {"Error": str(e)}


def add_video(file, title, description, tags, channel_id):
    """Adds a new entry in the videos table"""
    upload_date = datetime.datetime.now()
    extension = os.path.splitext(file.filename)[1]
    while True:
        video_id = idGenerator(8)
        if is_id_available(video_id):
            if file:
                file.save(os.path.join(
                          app.config['UPLOAD_FOLDER'],
                          video_id + extension
                          ))

            with engine.connect() as connection:
                try:
                    connection.execute(text("""INSERT INTO videos(id, title, description, tags, channel_id, upload_date) 
                                               VALUES (:video_id, :title, :description, :tags, :channel_id, :upload_date)"""),
                                     {'video_id': video_id, 'title': title, 'description': description,
                                               'tags': tags, 'channel_id': channel_id, 'upload_date': str(upload_date)})
                    connection.commit()
                    return {"Success": f"Video '{video_id}.mp4' added successfully to your channel."}
                except Exception as e:
                    return {"Error": str(e)}


def delete_comments(video_id):
    """Deletes all comments with the associated video id"""
    try:
        with engine.connect() as connection:
            connection.execute(text("DELETE FROM comments WHERE comments.video_id = :id"),
                                {"id": video_id})
            connection.commit()
        return None
    except Exception as e:
        return {f"Error": str(e)}


def add_comment(video_id, comment, user_id):
    """Adds a comment to the associated video id"""
    try:
        with engine.connect() as connection:
            connection.execute(text("INSERT INTO comments(comment, video_id, user_id) VALUES (:comment, :video_id, :user_id)"),
                                {"video_id": video_id, "comment": comment, "user_id": user_id})
            connection.commit()
        return {"Success": "Comment successfully added."}
    except Exception as e:
        return {f"Error": str(e)}


def delete_comment(comment_id):
    """Deletes comment with the associated comment id"""
    try:
        with engine.connect() as connection:
            connection.execute(text("DELETE FROM comments WHERE comments.id = :commentId"),
                                {"commentId": comment_id})
            connection.commit()
        return {"Success": "Comment successfully deleted."}
    except Exception as e:
        return {f"Error": str(e)}


def update_comment(comment_id, comment):
    """Updates comment with the associated comment id"""
    try:
        with engine.connect() as connection:
            connection.execute(text("UPDATE comments SET 'comment' = :comment WHERE comments.id = :commentId"),
                                {"commentId": comment_id, "comment": comment})
            connection.commit()
        return {"Success": "Comment successfully updated."}
    except Exception as e:
        return {f"Error": str(e)}


def delete_video(video_id):
    """Deletes a video and its comments from the database."""
    delete_comments(video_id)
    with engine.connect() as connection:
        try:
            connection.execute(text("DELETE FROM videos WHERE videos.id = :id"),
                                 {"id": video_id})
            connection.commit()
            return {"200": f"Video {video_id}.mp4  has been successfully deleted from your channel."}
        except Exception as e:
            return {f"Error": str(e)}


def update_video(video_id, title, description, tags):
    """Update a videos data in the database."""
    with engine.connect() as connection:
        try:
            connection.execute(text("""UPDATE videos SET 'title' = :title, 'description'= :description, 'tags'= :tags WHERE videos.id == :video_id"""),
                               {'video_id': video_id, 'title': title, 'description': description,
                                'tags': tags})
            connection.commit()
            return {"Success": "Video successfully updated."}
        except Exception as e:
            return {f"Error": str(e)}
