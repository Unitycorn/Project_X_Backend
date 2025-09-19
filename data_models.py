from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

db = SQLAlchemy()


class Channel(db.Model):
    __tablename__ = 'channel'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

    def __repr__(self):
        return f"Author(name = {self.name})"


class Video(db.Model):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    channel_id = Column(Integer, ForeignKey('authors.id'))

    def __repr__(self):
        return f"Video(title = {self.title}, channel_id = {self.channel_id})"
