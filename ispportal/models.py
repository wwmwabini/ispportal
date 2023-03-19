from ispportal import db, app, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def loaduser(user_id):
	return Clients.query.get(user_id)

class Clients(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	firstname = db.Column(db.String(50), nullable=False)
	lastname = db.Column(db.String(50), nullable=False)
	email = db.Column(db.String(500), nullable=False, unique=True)
	phone = db.Column(db.String(13), nullable=False, unique=True)
	username = db.Column(db.String(15), nullable=False, unique=True)
	password = db.Column(db.String(60), nullable=False)
	registrationdate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)