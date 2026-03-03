from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

db = SQLAlchemy()


class Channel(db.Model):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    name = Column(String)
    about = Column(String)
    logo_URL = Column(String)
    login_name = Column(String)
    password = Column(String)

    def __repr__(self):
        return f"User(name = {self.name})"


class Video(db.Model):
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    channel_id = Column(String, ForeignKey('users.id'))
    tags = Column(String)
    description = Column(String)
    views = Column(Integer)
    total_viewtime = Column(Integer)
    upload_date = Column(DateTime)

    def __repr__(self):
        return f"Video(title = {self.title}, channel_id = {self.channel_id})"


class Comment(db.model):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    comment = Column(String)
    user_id = Column(String, ForeignKey('users.id'))
    video_id = Column(String, ForeignKey('videos.id'))
    likes = Column(Integer)
    date = Column(DateTime)

    def __repr__(self):
        return f"Comment(comment = {self.comment}, user_id = {self.user_id})"


class Likes(db.model):
    __tablename__ = 'likes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'))
    video_id = Column(String, ForeignKey('videos.id'))

    def __repr__(self):
        return f"Like(user = {self.user_id}, video = {self.video_id})"


class Subscritions(db.model):
    __tablename__ = 'subs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String)
    channel = Column(String, ForeignKey('users.id'))

    def __repr__(self):
        return f"Sub(user = {self.user}, channel = {self.channel})"
