from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from data_manager import data_manager as video_manager, channel_manager as channel_manager
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import os
from data_models.models import db

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


with app.app_context():
    db.create_all()

CORS(app)

@app.route('/', methods=['GET'])
def index():
    """
    Get a fixed amount of random videos for the start page
    """
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    """
    Checks DB for user / password; returns success or error
    """
    login_name = request.json['email']
    password = request.json['password']
    return channel_manager.login(login_name, password)


@app.route('/register', methods=['POST'])
def register():
    name = request.json['name']
    file = request.json['image']
    about = request.json['description']
    login_name = request.json['login_name']
    password = request.json['password']
    return channel_manager.add_channel(file, name, about, login_name, password)


@app.route('/channel/<channel_id>', methods=['GET'])
def channel(channel_id):
    return channel_manager.get_channel(channel_id)


@app.route('/channel/delete/<channel_id>', methods=['POST'])
def delete_channel(channel_id):
    return channel_manager.remove_channel(channel_id)


@app.route('/channel/edit/<channel_id>', methods=['GET', 'POST'])
def edit_channel(channel_id):
    if request.method == 'POST':
        name = request.json['name']
        about = request.json['description']
        login_name = request.json['login_name']
        password = request.json['password']
        return channel_manager.edit_channel(channel_id, name, about, login_name, password)
    elif request.method == 'GET':
        return channel_manager.get_channel(channel_id)


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files['video']
        user_id = request.form['user_id']
        title = request.form['title']
        description = request.form['description']
        tags = request.form['tags']
        return video_manager.add_video(file, title, description, tags, user_id)


@app.route('/edit/<video_id>', methods=['GET', 'POST'])
def edit(video_id):
    if request.method == 'POST':
        title = request.json['title']
        description = request.json['description']
        tags = request.json['tags']
        return video_manager.update_video(video_id, title, description, tags)
    elif request.method == 'GET':
        return video_manager.load_video(video_id)


@app.route('/delete/<video_id>', methods=['POST'])
def delete(video_id):
    return video_manager.delete_video(video_id)


@app.route('/video/<video_id>', methods=['GET'])
def video(video_id):
    return video_manager.load_video(video_id)


@app.route('/video/<video_id>/comments', methods=['GET'])
def get_comments(video_id):
    return video_manager.load_comments(video_id)


@app.route('/video/<video_id>/comment/add', methods=['POST'])
def add_comment(video_id):
    return video_manager.add_comment(video_id, request.json['comment'], request.json['channelId'], request.json['date'])


@app.route('/comments/<comment_id>/delete', methods=['GET'])
def delete_comment(comment_id):
    return video_manager.delete_comment(comment_id)


@app.route('/comments/<comment_id>/update', methods=['POST'])
def update_comment(comment_id):
    return video_manager.update_comment(comment_id, request.json['comment'])


@app.route('/health', methods=['GET'])
def health():
    return {"status": "OK"}


@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({"error": "Method Not Allowed"}), 405


if __name__ == "__main__":
    # Launch the Flask dev server
    app.run(host="0.0.0.0", port=5000, debug=True)
