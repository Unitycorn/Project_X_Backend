from flask import Flask
import os
from data_models import db, Video, Channel
from sqlalchemy.orm import Session
from video_storage import video_storage as storage

app = Flask(__name__)

"""
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data/database.sqlite"
db.init_app(app)


engine = db.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
session = Session(engine)
"""


@app.route('/', methods=['GET'])
def index():
    """
    Get a fixed amount of random videos for the start page
    """
    return "Hi"


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Checks DB for user / password; returns success or error
    """
    pass


@app.route('/logout', methods=['POST'])
def logout():
    """
    resets active user
    """
    pass


@app.route('/register', methods=['POST'])
def register():
    """
    creates new account in DB, generating a new unique ID and logs user in
    """
    pass


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """
    create new ID and adds new video to DB
    """
    pass


@app.route('/edit/<video_id>', methods=['GET', 'POST'])
def edit(video_id):
    selected_video = storage.load_video(video_id)
    if not selected_video:
        return {"Error 404": "Video does not exist!"}
    else:
        return storage.update_video(selected_video)


@app.route('/delete/<video_id>', methods=['POST'])
def delete(video_id):
    return storage.delete_video(video_id)


@app.route('/channel/<channel_id>', methods=['GET'])
def channel(channel_id):
    pass


@app.route('/video/<video_id>', methods=['GET'])
def video(video_id):
    return storage.load_video(video_id)


if __name__ == "__main__":
    # Launch the Flask dev server
    app.run(host="0.0.0.0", port=5000, debug=True)
