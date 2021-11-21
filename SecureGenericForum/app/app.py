from flask import Flask
from flask import redirect
from flask import url_for
from flask import jsonify
from flask_login import LoginManager
from flask_login import login_required
from flask_sqlalchemy import SQLAlchemy
from app.config import *
from flask_wtf.csrf import CSRFProtect
import time


app = Flask(__name__, template_folder='../template', static_folder='../static')


if app.config["ENV"] == "Production":
    print("Using Production configs")
    app.config.from_object(ProductionConfig)
elif app.config["ENV"] == "Testing":
    print("Using Testing configs")
    app.config.from_object(TestConfig)
else: 
    print("Using Development configs")
    app.config.from_object(DevelopmentConfig)

login_manager = LoginManager()
login_manager.login_view = "api.user.login_page"
login_manager.init_app(app)
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

def wait_db_connection(engine):
    while True:
        try:
            with engine.connect() as conn:
                break
        except Exception as e:
            print(e)
            print("Sleeping")
            time.sleep(5)
wait_db_connection(db.engine)

@app.route("/")
@login_required
def index():
    return redirect(url_for("api.forum.home"))

@app.errorhandler(404) 
def invalid_route(e): 
    return "Invalid page", 404