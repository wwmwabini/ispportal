from ispportal import app, bcrypt, db
from flask import render_template, redirect, flash, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime, timedelta

from ispportal.forms import RegisterForm, LoginForm, ForgotUsername, ForgotPassword, RenewSubscriptionForm, ProfileForm
from ispportal.models import Clients, Plans, Subscriptions, News, Transactions, Payments
from ispportal.functions import (createusername, remindusernameviaemail, remindusernameviasms, welcomeemail, createsecurepassword, sendresetpassword, create_subscription,
	get_node_status, get_service_status, unsuspend_subscription, renewal_confirmation)

@app.route("/", methods=["GET", "POST"])
def home():
	return redirect('login')


@app.route("/register", methods=["GET", "POST"])
def register():

	plans = Plans.query.all()

	bronze_price, silver_price, gold_price = 0, 0, 0
	for p in plans:
		if p.name == 'bronze':
			bronze_price = int(p.price)
		elif p.name == 'silver':
			silver_price = int(p.price)
		else:
			gold_price = int(p.price)



	form = RegisterForm()

	if form.validate_on_submit():

		

		username = createusername(form.email.data)
		hashedpassword = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

		client = Clients(firstname=form.firstname.data, lastname=form.lastname.data, email=form.email.data, phone=form.phone.data, username=username, password=hashedpassword)
		db.session.add(client)
		db.session.commit()

		subscriber = Clients.query.filter_by(username=username).first()
		plan = Plans.query.filter_by(name=form.plan.data).first()



		#send client welcome emails
		try:
			print('username',username)
			remindusernameviaemail(form.email.data, username)
			welcomeemail(form.email.data, form.firstname.data, username)
		except Exception as e:
			print(e)


		#create subscription. will be updated to create only after payment is successful
		try:
			create_subscription(username, subscriber.id, plan.id, form.email.data)
		except Exception as e:
			print(e)

		message = "Thank you for registering. You can now login using your generated username: " + username
		flash(message, 'success')

		return redirect('login')

	return render_template('auth/register.html', title='Register', form=form, plans=plans, bronze_price=bronze_price, silver_price=silver_price, gold_price=gold_price)


@app.route("/login", methods=["GET", "POST"])
def login():

	form = LoginForm()

	if form.validate_on_submit():

		user = Clients.query.filter_by(username=form.username.data).first()

		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			
			redirect_page = request.args.get('next')

			if redirect_page:
				return redirect(redirect_page)
			else:
				welcomemessage = 'Welcome back ' + user.username
				flash(welcomemessage, 'success')
				return redirect(url_for('dashboard'))
		else:
			flash('Invalid username or password.', 'danger')
			return redirect(url_for('login'))

	return render_template('auth/login.html', title='Login', form=form)


@app.route("/customer/forgotusername", methods=["GET", "POST"])
def forgotusername():

	form = ForgotUsername()

	if form.validate_on_submit():
		user = Clients.query.filter_by(phone=form.phone.data).first()

		if user:
			try:
				remindusernameviasms(user.phone, user.username)
				remindusernameviaemail(user.email, user.username)
				flash('We have sent you further instructions on phone and email. Please check.', 'info')
			except Exception as e:
				print(e)
				flash('We could not send the username reminder due to errors on our side. Please try again later or contact support', 'warning')
				return redirect(url_for('forgotusername'))
			
		return redirect(url_for('forgotusername'))


	return render_template('auth/forgotusername.html', title='Forgot Username', form=form)



@app.route("/customer/forgotpassword", methods=["GET", "POST"])
def forgotpassword():

	form = ForgotPassword()

	if form.validate_on_submit():
		user = Clients.query.filter_by(username=form.username.data).first()

		if user:
			password = createsecurepassword()
			hashedpassword = bcrypt.generate_password_hash(password).decode('utf-8')

			user.password = hashedpassword
			db.session.commit()

			sendresetpassword(user.email, password)
			flash('We have sent you a temporary password to your email. Please check.', 'info')

			return redirect('forgotpassword')
		else:
			flash('Invalid username. Please try again.', 'danger')
			return redirect('forgotpassword')

	return render_template('auth/forgotpassword.html', title='Forgot Password', form=form)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
	logout_user()
	flash('You have been successfully logged out', 'success')
	return redirect(url_for('login'))




@app.route("/customer/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
	subscription = Subscriptions.query.filter_by(client_id=current_user.id).first()
	servicestatus = get_service_status(subscription.vmid)
	nodestatus = get_node_status(subscription.node)
	news = News.query.order_by(News.created_at.desc()).limit(3).all()

	return render_template('dashboard/dashboard.html', title='Dashboard', subscription=subscription, servicestatus=servicestatus, nodestatus=nodestatus, news=news)


@app.route("/customer/subscription/renew", methods=["GET", "POST"])
@login_required
def renew_subscription():

	subscription = Subscriptions.query.filter_by(client_id=current_user.id).first()

	form = RenewSubscriptionForm()

	if form.validate_on_submit():
		mpesacode = form.paymentreference.data.upper()
		transaction = Transactions.query.filter_by(transaction_id=mpesacode).first()

		if not transaction:
			flash('Payment has not been received yet. Try again after a minute', 'warning')
			return redirect(url_for('renew_subscription'))
		else:
			if transaction.claimed is True:
				flash('The transaction has already been claimed.', 'danger')
				return redirect(url_for('renew_subscription'))
			else:

				"""
				- check if amount paid is enough, if should not be claimed
				- check if service status is suspended and unsuspend
				- notify client on successful renewal
				- show flash message
				"""

				sub = Subscriptions.query.filter_by(id=subscription.id).first() # this should be updated in the future if a client can have > 1 subscriptions

				transaction.claimed = True
				sub.expirydate=sub.expirydate + timedelta(days=30)
				
				if subscription.status == 'stopped':
					unsuspend_subscription(subscription.vmid)
				renewal_confirmation(current_user.id, subscription.id, transaction.id)

				db.session.commit() #commit to db only after all above events have occured.

				flash('Service renewed successfully. Thank you for your continued business and support', 'success')
				
				


	return render_template('dashboard/renew_subscription.html', title="Subscription Renewal", subscription=subscription, form=form)


@app.route("/customer/profile", methods=["GET", "POST"])
@login_required
def profile():

	client = Clients.query.filter_by(id=current_user.id).first()

	form = ProfileForm()

	if form.validate_on_submit():
		user_email_check = Clients.query.filter_by(email=form.email.data).first()
		user_phone_check = Clients.query.filter_by(phone=form.phone.data).first()

		if client.email == form.email.data and client.firstname == form.firstname.data and client.lastname == form.lastname.data and client.phone == form.phone.data:
			flash('You must update at least one field before saving changes.', 'warning')
			return redirect(url_for('profile'))
		elif user_email_check and user_email_check.id != current_user.id: #check if user w/ submitted email exists, and is not equal to current user.
			flash('The email address submitted is already in use in our system. Please try again', 'warning')
			return redirect(url_for('profile'))
		elif user_phone_check and user_phone_check.id != current_user.id: #check if user w/ submitted phone exists, and is not equal to current user.
			flash('The phone number submitted is already in use in our system. Please try again', 'warning')
			return redirect(url_for('profile'))
		else:
			client.firstname = form.firstname.data
			client.lastname = form.lastname.data
			client.email = form.email.data
			client.phone = form.phone.data

			db.session.commit()
			flash('Your details have been successfully updated.', 'success')
			return redirect(url_for('profile'))


	return render_template('dashboard/profile.html', title="My Profile", form=form)

@app.route("/customer/activity/transactions", methods=["GET", "POST"])
@login_required
def transactions():
	return render_template('dashboard/transactions.html', title="Transaction History")

@app.route("/customer/activity/datausage", methods=["GET", "POST"])
@login_required
def datausage():
	return render_template('dashboard/datausage.html', title="Data Usage")


@app.route("/customer/subscription/credit", methods=["GET", "POST"])
@login_required
def managecredit():
	return render_template('dashboard/managecredit.html', title="Manage Credit")