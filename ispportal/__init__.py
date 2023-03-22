import os

from flask import Flask, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate

from dotenv import load_dotenv


load_dotenv()


app = Flask(__name__)


#database
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////home/mwabini/ispportal.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


#smtp
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')


db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
mail = Mail(app)


@login_manager.unauthorized_handler
def unauthorized():
    flash("Please login first to access that resource.", "info")
    return redirect(url_for('login'))


from ispportal import routes
import api_v1