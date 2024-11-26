from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.app_context().push()
app.config['SECRET_KEY'] = 'aldcb7e926bf72ac2b35f9c6'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
#user is redirected to login
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"

from market import routes
