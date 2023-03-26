from ispportal import db, app, login_manager
from datetime import datetime, timedelta
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
	region = db.Column(db.Enum('Thika'), nullable=False, server_default="Thika")
	subscriptions = db.relationship('Subscriptions', backref='client')

class Subscriptions(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	orderdate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	expirydate = db.Column(db.DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(days=30))
	hostname = db.Column(db.String(100))
	node = db.Column(db.String(100))
	vmid = db.Column(db.Integer, nullable=False, unique=True)
	password = db.Column(db.String(60))
	status = db.Column(db.Enum('pending','suspended','stopped','deleted','running','unknown'), nullable=False, server_default="pending")
	client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
	plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'))

class Plans(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	name = db.Column(db.String(10), nullable=False, unique=True)
	price = db.Column(db.Numeric(precision=8, scale=2), nullable=True)
	ostemplate = db.Column(db.String(100))
	bwlimit = db.Column(db.Integer, default=0)
	cores = db.Column(db.Integer)
	memory = db.Column(db.Integer)
	start = db.Column(db.Integer, default=1)
	rootfs = db.Column(db.String(100))
	storage = db.Column(db.String(100))
	ostype = db.Column(db.String(100), default='ubuntu')
	subscriptions = db.relationship('Subscriptions', backref='plan')

class Nodes(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	name = db.Column(db.String(100), nullable=False, unique=True)
	ipv4address = db.Column(db.String(12), nullable=False, unique=True)
	ipv6address = db.Column(db.String(256), nullable=False, unique=True)
	status = db.Column(db.Enum('online', 'offline', 'unknown'), nullable=False, server_default='unknown')
	create_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	last_update = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

class News(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	author = db.Column(db.String(100), nullable=False, default='Admin')
	title = db.Column(db.String(500), nullable=False)
	content = db.Column(db.Text, nullable=False)
	category = db.Column(db.Enum('Announcement', 'News', 'Update', 'Alert'), nullable=False, default='Announcement')
	created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	last_update = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    claimed = db.Column(db.Boolean, nullable=False, default=False)
    invoice_id = db.Column(db.String(50), nullable=True)
    transaction_id = db.Column(db.String(50), nullable=False) #Does Intasend return this field, mpesa transaction id?
    state = db.Column(db.String(50), nullable=False, default='PROCESSING')
    provider = db.Column(db.String(50), nullable=False, default='M-PESA')
    charges = db.Column(db.Integer, nullable=True)
    net_amount = db.Column(db.Integer, nullable=True)
    currency = db.Column(db.String(50), nullable=False, default='KES')
    value = db.Column(db.Integer, nullable=True)
    account = db.Column(db.String(50), nullable=True)
    api_ref = db.Column(db.String(50), nullable=True)
    host = db.Column(db.String(100), nullable=True)
    failed_reason = db.Column(db.String(500), nullable=True)
    failed_code = db.Column(db.String(50), nullable=True)
    failed_code_link = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.String(100), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.String(100), nullable=False, default=datetime.utcnow)


class Payments():
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	client_id = db.Column(db.Integer, nullable=False)
	transaction_id = db.Column(db.Integer, nullable=False)


