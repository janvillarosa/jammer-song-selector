import os

from flask import Flask, render_template
from flask_compress import Compress
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix

# Set working directory to project root
os.chdir(os.path.abspath(os.path.dirname(__file__)))

# If available, load environment variables from .env before rest of the package
if os.path.isfile(".env"):
    from dotenv import load_dotenv

    load_dotenv()


########################################################################################################################
# Setup / Configuration
########################################################################################################################

# Instantiate app
application = Flask(__name__)
db_conn_string = os.environ["DB_CONN_STRING"]
application.config["SQLALCHEMY_DATABASE_URI"] = db_conn_string
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
application.config["SECRET_KEY"] = os.environ["APP_SECRET"]
application.wsgi_app = ProxyFix(application.wsgi_app)  # Fixes Swagger UI issues over HTTPS

from database import db
db.init_app(application)

# Add extensions
CORS(application)
Compress(application)

from controller import api
api.init_app(application)

def create_db():
    db.create_all()


########################################################################################################################
# Run / Debug
########################################################################################################################

@application.route("/")
def index():
    return render_template("index.html", **{"greeting": "Hello from Flask!"})

if __name__ == "__main__":
    if os.getenv("FLASK_ENV") == "development":
        application.run()