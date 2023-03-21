import requests
import os

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
	pass

@app.route("/api/v1/suspend_subscription", methods=["PUT"])
def suspend_subscription():
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