from flask_sqlalchemy import SQLAlchemy
import mysql.connector
import os

db = SQLAlchemy()

def init_db(app):

   with app.app_context():
      #db.drop_all()
      db.create_all()
     