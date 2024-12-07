from flask import Flask
from dotenv import load_dotenv
from utils.db import db,init_db
from views.Heladeria_controller import heladeria_routes
from views.API import heladeria_apis
from flask_restful import Api
import pymysql
import os


load_dotenv(override=True)
app = Flask(__name__)
pymysql.install_as_MySQLdb()

secret_key = os.urandom(24)
app.config['SECRET_KEY'] = secret_key

db_user = os.getenv("MYSQLUSER")
db_password = os.getenv("MYSQLPASSWORD")
db_host = os.getenv("MYSQLHOST")
db_port = os.getenv("MYSQLPORT")
db_name = os.getenv("MYSQLDATABASE")

app.config["SQLALCHEMY_DATABASE_URI"]= f"mysql+pymysql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)#SQLAlchemy(app)
init_db(app)
api = Api(app)

heladeria_routes(app)
heladeria_apis(api)

if __name__ == "__main__":
    app.run(debug=True)