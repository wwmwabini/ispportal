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
	subscriptions = db.relationship('Clients', backref='subscriber')

class Subscriptions(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	orderdate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	#plan = db.Column(db.String(10), nullable=False, unique=True)
	hostname = db.Column(db.String(100))
	node = db.Column(db.String(100))
	vmid = db.Column(db.Integer, nullable=False, unique=True)
	password = db.Column(db.String(60))
	status = db.Column(db.Enum('pending','stopped','deleted','active'), nullable=False, server_default="pending")
	client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
	plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'))

class Plans(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	name = db.Column(db.String(10), nullable=False, unique=True)
	ostemplate = db.Column(db.String(100))
	bwlimit = db.Column(db.Integer, default=0)
	cores = db.Column(db.Integer)
	memory = db.Column(db.Integer)
	start = db.Column(db.Integer, default=1)
	rootfs = db.Column(db.String(100))
	storage = db.Column(db.String(100))
	ostype = db.Column(db.String(100), default='ubuntu')
	subscriptions = db.relationship('Plans', backref='plan')
