import requests
import os
import random, secrets, string

from ispportal import app
from flask import Flask, request, json, jsonify
from dotenv import load_dotenv

load_dotenv()


proxmox_host = os.environ.get('PROXMOX_HOST')
proxmox_username = os.environ.get('PROXMOX_USERNAME')
proxmox_password = os.environ.get('PROXMOX_PASSWORD')
proxmox_port = os.environ.get('PROXMOX_PORT')
proxmox_api_token = os.environ.get('PROXMOX_API_TOKEN')

proxmox_base_endpoint = 'https://'+proxmox_host+':'+proxmox_port

#these details should be moved to register page, they should be sent to api from
#order form
proxmox_node = 'pve'
proxmox_ostemplate = 'local:vztmpl/ubuntu-20.04-standard_20.04-1_amd64.tar.gz'
proxmox_vmid = random.randint(1,9999)
proxmox_bwlimit = 0
proxmox_cores = 1
proxmox_hostname = proxmox_vmid
proxmox_memory = 512
proxmox_password = ''.join((secrets.choice(string.ascii_letters + string.digits) for i in range(10)))
proxmox_start = 1
proxmox_rootfs = 'local-lvm:8'
proxmox_storage = 'local-lvm'
proxmox_ostype = 'ubuntu'



#Deprecated route. We use proxmox_api_token instead of ticket and csrftoken
@app.route("/api/v1/accesstokens", methods=["GET"])
def get_access_tokens():
	api_endpoint = '/api2/json/access/ticket'
	params = {
		'username':proxmox_username, 
		'password':proxmox_password
	}
	headers = {

	}
	access_tokens_endpoint = proxmox_base_endpoint+api_endpoint

	response = requests.post(access_tokens_endpoint,params=params,verify=False).json()

	credentials = {
	'CSRFPreventionToken': response['data']['CSRFPreventionToken'],
	'ticket': response['data']['ticket']

	}

	return credentials



@app.route("/api/v1/create_subscription", methods=["POST"])
def create_subscription():
	#create sub, return sub details to calling function

	api_endpoint = '/api2/json/nodes/'+proxmox_node+'/lxc'
	url = proxmox_base_endpoint+api_endpoint

	headers = {
	'Authorization': proxmox_api_token
	}

	features = {
	'node':proxmox_node,
	'ostemplate':proxmox_ostemplate,
	'vmid':proxmox_vmid,
	'bwlimit':proxmox_bwlimit,
	'cores':proxmox_cores,
	'hostname':proxmox_hostname,
	'memory':proxmox_memory,
	'password':proxmox_password,
	'start':proxmox_start,
	'rootfs':proxmox_rootfs,
	'storage':proxmox_storage,
	'ostype':proxmox_ostype

	}

	response = requests.post(url, params=features,headers=headers,verify=False)

	print(response.text)

	return response.text




@app.route("/api/v1/suspend_subscription", methods=["PUT"])
def suspend_subscription():
	pass

@app.route("/api/v1/reactivate_subscription", methods=["PUT"])
def reactivate_subscription():
	pass

@app.route("/api/v1/upgrade_subscription", methods=["PUT"])
def upgrade_subscription():
	pass 

@app.route("/api/v1/terminate_subscription", methods=["DELETE"])
def terminate_subscription():
	pass

@app.route("/api/v1/get_subscription_details", methods=["GET"])
def get_subscription_details():
	pass