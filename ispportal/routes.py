from ispportal import app, bcrypt, db
from flask import render_template, redirect, flash, url_for, request
from flask_login import login_user, logout_user, current_user, login_required

from ispportal.forms import RegisterForm, LoginForm, ForgotUsername, ForgotPassword
from ispportal.models import Clients
from ispportal.functions import createusername, remindusernameviaemail, remindusernameviasms, welcomeemail, createsecurepassword, sendresetpassword

@app.route("/", methods=["GET", "POST"])
def home():
	return redirect('login')


@app.route("/register", methods=["GET", "POST"])
def register():

	form = RegisterForm()

	if form.validate_on_submit():

		username = createusername(form.email.data)
		hashedpassword = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

		user = Clients(firstname=form.firstname.data, lastname=form.lastname.data, email=form.email.data, phone=form.phone.data, username=username, password=hashedpassword)
		db.session.add(user)
		db.session.commit()

		try:
			remindusernameviaemail(form.email.data, username)
			welcomeemail(form.email.data, form.firstname.data, username)
		except Exception as e:
			print(e)

		message = "Thank you for registering. You can now login using your generated username: " + username
		flash(message, 'success')

		return redirect('login')

	return render_template('auth/register.html', title='Register', form=form)


@app.route("/login", methods=["GET", "POST"])
def login():

	form = LoginForm()

	if form.validate_on_submit():

		user = Clients.query.filter_by(username=form.username.data).first()

		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			welcomemessage = 'Welcome back ' + user.username
			flash(welcomemessage, 'success')
			redirect_page = request.args.get('next')

			if redirect_page:
				return redirect(redirect_page)
			else:
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




@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
	return render_template('dashboard/dashboard.html', title='Dashboard')


@app.route("/customer/profile", methods=["GET", "POST"])
@login_required
def profile():
	return render_template('dashboard/profile.html', title="My Profile")

@app.route("/customer/activity/transactions", methods=["GET", "POST"])
@login_required
def transactions():
	return render_template('dashboard/transactions.html', title="Transaction History")

@app.route("/customer/activity/datausage", methods=["GET", "POST"])
@login_required
def datausage():
	return render_template('dashboard/datausage.html', title="Data Usage")

@app.route("/customer/subscription/renew", methods=["GET", "POST"])
@login_required
def renew_subscription():
	return render_template('dashboard/renew_subscription.html', title="Subscription Renewal")

@app.route("/customer/subscription/credit", methods=["GET", "POST"])
@login_required
def managecredit():
	return render_template('dashboard/managecredit.html', title="Manage Credit")