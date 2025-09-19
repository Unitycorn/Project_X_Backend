from urllib import request
from flask import Flask, render_template, request, redirect
import os
from data_models import db, Video, Channel
from sqlalchemy import asc, desc, ColumnElement
from sqlalchemy.orm import Session

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/database.sqlite')}"
db.init_app(app)


engine = db.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
session = Session(engine)


@app.route('/', methods=['GET', 'POST'])
def index():
    pass
