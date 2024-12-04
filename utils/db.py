from flask_sqlalchemy import SQLAlchemy, g, current_app
import mysql.connector

db = SQLAlchemy()
g.db = mysql.connector.connect(port=current_app.config["DATABASE_PORT"],)

def init_db(app):

   with app.app_context():
      #db.drop_all()
      db.create_all()
     