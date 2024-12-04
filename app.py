from flask import Flask
from dotenv import load_dotenv
from utils.db import db,init_db
from views.Heladeria_controller import heladeria_routes
from views.API import heladeria_apis
from flask_restful import Api
import os

load_dotenv(override=True)
app = Flask(__name__)

secret_key = os.urandom(24)
app.config['SECRET_KEY'] = secret_key

app.config["SQLALCHEMY_DATABASE_URI"]= f"mysql+pymysql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config.from_mapping(DATABASE_PORT= os.environ.get('FLASK_DATABASE_PORT'))

db.init_app(app)#SQLAlchemy(app)
init_db(app)
api = Api(app)

heladeria_routes(app)
heladeria_apis(api)

if __name__ == "__main__":
    app.run(debug=True)