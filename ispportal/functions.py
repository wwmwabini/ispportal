import random, re, os, requests, secrets, string

from ispportal.models import Clients
from flask import render_template
from flask_mail import Message
from dotenv import load_dotenv

from ispportal import mail

load_dotenv()

#Create random username on registration of new account
def createusername(email):

	emailwithoutsymbols = re.sub('\W+','', email)

	username = emailwithoutsymbols[0:3] + str(random.randint(1000,9999))

	check = Clients.query.filter_by(username=username).first()

	if check:
		createusername(email)
	else:
		return username


#Create random password
def createsecurepassword():
	securepassword = ''.join((secrets.choice(string.ascii_letters + string.digits + string.punctuation) for i in range(10)))
	return securepassword



#Registration welcome message
def welcomeemail(email, firstname, username):
	msg = Message("Your ISP Portal Details", sender=(os.environ.get('MAIL_DEFAULT_SENDER_NAME'), os.environ.get('MAIL_DEFAULT_SENDER')), recipients=[email])
	msg.html = render_template('auth/message_register.html', firstname=firstname, login_url=login_url,username=username)
	msg.reply_to = os.environ.get('MAIL_DEFAULT_SENDER')
	mail.send(msg)

	return 0

#Send username reminder via email
def remindusernameviaemail(email, username):
	msg = Message("Your ISP Portal Username", sender=(os.environ.get('MAIL_DEFAULT_SENDER_NAME'), os.environ.get('MAIL_DEFAULT_SENDER')), recipients=[email])
	msg.html = render_template('auth/message_forgotusername.html', username=username)
	msg.reply_to = os.environ.get('MAIL_DEFAULT_SENDER')
	mail.send(msg)

	return 0

#Send password reset via email
def sendresetpassword(email, password):
	msg = Message("Your ISP Portal temporary password", sender=(os.environ.get('MAIL_DEFAULT_SENDER_NAME'), os.environ.get('MAIL_DEFAULT_SENDER')), recipients=[email])
	msg.html = render_template('auth/message_pwreset.html', password=password)
	msg.reply_to = os.environ.get('MAIL_DEFAULT_SENDER')
	mail.send(msg)

	return 0

#Send username via sms
def remindusernameviasms(phone, username):
	message = "Your username for ISP Portal is " + username
	jisort_username = os.environ.get('JISORT_SMS_USERNAME')
	jisort_password = os.environ.get('JISORT_SMS_PASSWORD')
	endpoint = "https://my.jisort.com/messenger/send_message/"+"?username="+jisort_username+"&password="+jisort_password+"&recipients="+phone+"&message="+message
	payload = {}
	headers = {}
	response = requests.request("GET", endpoint, headers=headers, data=payload)

	return 0



