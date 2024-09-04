from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import stripe
import os

app = Flask(__name__)

# Secret key for Flask sessions
app.config['SECRET_KEY'] = 'supersecretkey'

# Setting up the database URI for SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Initialize the extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User loader function for Flask-Login
from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Stripe configuration (assumed to be loaded from environment variables)
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

from app import routes
