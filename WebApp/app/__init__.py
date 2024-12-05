from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

csrf = CSRFProtect(app)

# initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access this page."

# load User model and set user_loader function
from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from app import views, models