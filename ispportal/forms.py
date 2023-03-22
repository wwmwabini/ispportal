from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

from ispportal.models import Clients

class RegisterForm(FlaskForm):
	plan = BooleanField("To register, you must subscribe to a package. Select one below:")
	firstname = StringField("First Name", validators=[DataRequired(), Length(min=2, max=50)])
	lastname = StringField("Last Name", validators=[DataRequired(), Length(min=2, max=50)])
	email = EmailField("Email Address", validators=[DataRequired(), Length(min=4, max=100)])
	phone = StringField("Phone", validators=[DataRequired(), Length(min=10, max=10)])
	password = PasswordField("Password", validators=[DataRequired()])
	confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField("Register")

	def validate_email(form, email):
		emailaddress = Clients.query.filter_by(email=email.data).first()
		if emailaddress:
			raise ValidationError("Email already in use. Please use a diffrent email.")

	def validate_phone(form, phone):
		phonenumber = Clients.query.filter_by(phone=phone.data).first()
		if phonenumber:
			raise ValidationError("Phone number is already in use. Please use a diffrent phone number.")

	def validate_password(form, password):
		digits, uppercase, lowercase = 0, 0, 0

		if len(password.data) >= 10:
			for character in password.data:
				if character.isdigit():
					digits+=1
				if character.isupper():
					uppercase+=1
				if character.islower():
					lowercase+=1

			if digits < 1 or uppercase < 1 or lowercase < 1:
				raise ValidationError("Password must be at least 10 characters long and contain lowercase, uppercase and digit characters.")
		else:
			raise ValidationError("Password must be at least 10 characters long and contain lowercase, uppercase and digit characters.")



class LoginForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	remember = BooleanField("Remember Me")
	submit = SubmitField("Login")


class ForgotUsername(FlaskForm):
	phone = StringField("Enter your phone", validators=[DataRequired(), Length(min=10, max=10)])
	submit = SubmitField('Remind Username')

	def validate_phone(form, phone):
		phonenumber = Clients.query.filter_by(phone=phone.data).first()
		if not phonenumber:
			raise ValidationError("Phone number does not exist in our system. Please try again.")


class ForgotPassword(FlaskForm):
	username = StringField("Enter your username", validators=[DataRequired()])
	submit = SubmitField('Reset Password')

	def validate_username(form, username):
		username = Clients.query.filter_by(username=username.data).first()
		if not username:
			raise ValidationError('Username does not exist in our system. Please try again')