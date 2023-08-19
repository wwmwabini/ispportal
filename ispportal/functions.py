import random, re, os, requests, secrets, string, time, json
import timeout_decorator

from ispportal.models import Clients, Plans, Subscriptions, Transactions

from flask import render_template, jsonify
from flask_mail import Message
from dotenv import load_dotenv
from datetime import datetime
from PIL import Image

from ispportal import mail, app, bcrypt, db, scheduler

load_dotenv()


#overrall variables
proxmox_host = os.environ.get('PROXMOX_HOST')
proxmox_port = str(os.environ.get('PROXMOX_PORT'))
proxmox_apitoken = os.environ.get('PROXMOX_API_TOKEN')
proxmox_node = 'pve'

#Create random username on registration of new account
def createusername(email):

	emailwithoutsymbols = re.sub('\W+','', email)

	username = emailwithoutsymbols[0:3] + str(random.randint(1000,9999))

	check = Clients.query.filter_by(username=username).first()

	if check:
		createusername(email)
	else:
		return username


#Create random password for client area login
def createsecurepassword():
	securepassword = ''.join((secrets.choice(string.ascii_letters + string.digits + string.punctuation) for i in range(10)))
	return securepassword


#Create a random unique vmid
def create_vmid():
	vmid = random.randint(200,9999)
	sub = Subscriptions.query.filter_by(vmid=vmid).first()

	if sub:
		create_vmid()
	else:
		return vmid

#Create a subscription
def create_subscription(username, clientid, planid, clientemail):

	proxmox_password = ''.join((secrets.choice(string.ascii_letters + string.digits + string.punctuation) for i in range(10)))
	plan_details = Plans.query.filter_by(id=planid).first()


	headers = {
	'Authorization': proxmox_apitoken
	}

	params = {

	'hostname': username + '.rawle.local',
	'node': proxmox_node,
	'vmid': create_vmid(),
	'password': proxmox_password,
	'ostemplate': plan_details.ostemplate,
	'bwlimit': plan_details.bwlimit,
	'cores': plan_details.cores,
	'memory': plan_details.memory,
	'start': plan_details.start, 
	'rootfs': plan_details.rootfs,
	'storage': plan_details.storage,
	'ostype': plan_details.ostype

	}

	#send email confirmation containing success message, username, password and subscription details
	hashedpassword = bcrypt.generate_password_hash(proxmox_password).decode('utf-8')
	status = 'pending'

	creation_endpoint = '/api2/json/nodes/'+proxmox_node+'/lxc'
	url1 = 'https://'+proxmox_host + ':' + proxmox_port + creation_endpoint

	

	sub = Subscriptions(
		orderdate=datetime.now(),
		hostname = params['hostname'],
		node = params['node'],
		vmid = params['vmid'],
		password = hashedpassword,
		status = status,
		client_id = clientid,
		plan_id = planid
	)
	db.session.add(sub)
	db.session.commit()

	response = requests.post(url1, params=params,headers=headers,verify=False)

	print('response.status_code', response.status_code)


	if response.status_code == 200:
		print('success')
		sendorderconfirmation(params['vmid'], params['password'], plan_details.name, clientemail)
	else:
		print('error status code:', response.status_code, response.text)


	time.sleep(30)

	#get vm status after seconds above
	status_endpoint = '/api2/json/nodes/'+proxmox_node+'/lxc/'+str(params['vmid'])+'/status/current'
	url2 = 'https://'+proxmox_host + ':' + proxmox_port + status_endpoint
	service_data = requests.get(url2, headers=headers, verify=False) # returns stopped|running, among other things as a string.

	json_service_data = json.loads(service_data.text)
	service_status = json_service_data['data']['status']



	if service_status == 'running':
		sub = Subscriptions.query.filter_by(vmid=params['vmid']).first()
		sub.status = 'running'
		db.session.commit()
	else:
		print('Service is in stopped status! Contact admin')

	return response.text



def get_subscription_details(vmid):
	pass


#Get the status of the node, whether online or offline etc
@timeout_decorator.timeout(2, use_signals=False)
def get_node_status(node):

	#node_endpoint = '/api2/json/nodes/'+node+'/status'
	node_endpoint = '/api2/json/cluster/status'
	url = 'https://'+proxmox_host + ':' + proxmox_port + node_endpoint

	headers = {
	'Authorization': proxmox_apitoken
	}

	try:
		node_data = requests.get(url, headers=headers, verify=False)
		json_node_data = json.loads(node_data.text)
		node_status_boolean = json_node_data['data'][0]['online']
		if node_status_boolean == 1:
			node_status = 'online'
		else:
			node_status = 'offline'
	except Exception as e:
		return 'offline'

	return node_status


#Get the status of the vm/service, whether online or offline etc
@timeout_decorator.timeout(2, use_signals=False)
def get_service_status(vmid):

	service_endpoint = '/api2/json/nodes/'+proxmox_node+'/lxc/'+str(vmid)+'/status/current'
	url = 'https://'+proxmox_host + ':' + proxmox_port + service_endpoint

	headers = {
	'Authorization': proxmox_apitoken
	}

	try:
		service_data = requests.get(url, headers=headers, verify=False)

		json_service_data = json.loads(service_data.text)
		status = json_service_data['data']['status']
		print('status', status)
		if status == 'running':
			service_status = 'running'
		else:
			service_status = 'stopped'
			print(service_status)
	except Exception as e:
		return 'unknown'

	return service_status

#Unsuspend susbcription
def unsuspend_subscription(vmid):

	service_endpoint = '/api2/json/nodes/'+proxmox_node+'/qemu/'+str(vmid)+'/status/start'
	url = 'https://'+proxmox_host + ':' + proxmox_port + service_endpoint

	headers = {
	'Authorization': proxmox_apitoken
	}

	params = {

	'node': proxmox_node,
	'vmid': vmid
	}


	response = requests.post(url, params=params,headers=headers,verify=False)


	if response.status_code == 200:
		return 200
	else:
		print('error status code:', response.status_code, response.text)
		return response.status_code






'''
SMS AND EMAIL SENDING FUNCTIONS START HERE
'''


#Registration welcome message
def welcomeemail(email, firstname, username):
	msg = Message("Your ISP Portal Details", sender=(os.environ.get('MAIL_DEFAULT_SENDER_NAME'), os.environ.get('MAIL_DEFAULT_SENDER')), recipients=[email])
	msg.html = render_template('auth/message_register.html', firstname=firstname, login_url=os.environ.get("BASE_URL"),username=username)
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

#Send order setup completed confirmation
def sendorderconfirmation(vmid, password, plan, email):
	subscription = Subscriptions.query.filter_by(vmid=vmid).first()
	client = Clients.query.filter_by(email=email).first()

	expirydate = subscription.expirydate.strftime('%d/%m/%Y')



	msg = Message("Order Completed", sender=(os.environ.get('MAIL_DEFAULT_SENDER_NAME'), os.environ.get('MAIL_DEFAULT_SENDER')), recipients=[email])
	msg.html = render_template('dashboard/message_ordercompleted.html', firstname=client.firstname, lastname=client.lastname,  
		hostname=subscription.hostname, password=password,
		plan=subscription.plan.name, expirydate=expirydate)
	msg.reply_to = os.environ.get('MAIL_DEFAULT_SENDER')
	mail.send(msg)


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

#Renewal confirmation message
def renewal_confirmation(client_id, subscription_id, transaction_id):
	user = Clients.query.filter_by(id=client_id).first()
	sub = Subscriptions.query.filter_by(id=subscription_id).first()
	transaction = Transactions.query.filter_by(id=transaction_id).first()

	msg = Message("Subscription Renewal Confirmation", sender=(os.environ.get('MAIL_DEFAULT_SENDER_NAME'), os.environ.get('MAIL_DEFAULT_SENDER')), recipients=[user.email])
	msg.html = render_template('dashboard/message_renewalconfirmation.html', subscription_hostname=sub.hostname, subscription_expirydate=sub.expirydate, transaction_reference=transaction.transaction_id, date_paid=transaction.updated_at)
	msg.reply_to = os.environ.get('MAIL_DEFAULT_SENDER')
	mail.send(msg)

	return 0



"""
OTHER FUNCTIONS
"""

#Downgrade Scheduler
def downgrade_scheduler(subscription_id, new_plan_id):
	print("INFO::Commencing downgrade for subscription ID ", subscription_id, "...")
	with app.app_context():
		sub = Subscriptions.query.filter_by(id=subscription_id).first()

		sub.plan_id = new_plan_id
		db.session.commit()

		#Write code to call proxmox and reduce resources for VM
		#Write code to send confirmation email to owner once process succeeds 

		print("INFO::Downgrade completed.")

	return 0


#Function to check if job schedule was done successfully
def downgrade_scheduler_listener():
	pass


#Upgrade
def do_upgrade(subscription_id, new_plan_id):
	print("INFO::Commencing upgrade for subscription ID ", subscription_id, "...")
	with app.app_context():
		sub = Subscriptions.query.filter_by(id=subscription_id).first()

		sub.plan_id = new_plan_id
		db.session.commit()

		#Write code to call proxmox and increase resources for VM
		#Write code to schedule deduction of money from payment gateway or suspend service if unable to deduct for a while
		#Write code to send confirmation email to owner once process succeeds 

		print("INFO::Upgrade completed.")


#Profile Picture
def save_picture(picture_from_form):
	random_pic_name = secrets.token_hex(42)
	_, pic_extension = os.path.splitext(picture_from_form.filename)
	picture_name = random_pic_name + pic_extension
	picture_path = os.path.join(app.root_path, 'static/img/profile_pics', picture_name)

	img = resize_picture(picture_from_form)

	img.save(picture_path)

	return picture_name

def resize_picture(picture_from_form):
	output_size = (250,250)
	image = Image.open(picture_from_form)
	image.thumbnail(output_size)
	
	return image


def delete_old_picture(old_picture_path):
	if os.path.isfile(old_picture_path):
		try:
			os.remove(old_picture_path)
		except Exception as e:
			print('Error. Could not delete file.', e)
