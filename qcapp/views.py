from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login

import os

import MySQLdb

# These environment variables are configured in app.yaml.
# Not sure how app.yaml is actually supposed to hook up -
# For now, load in values directly
# CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
# CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
# CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')
CLOUDSQL_CONNECTION_NAME = 'quickcanvass:us-central1:quickcanvass'
CLOUDSQL_USER = 'root'
CLOUDSQL_PASSWORD = 'cos333'
cloudsql_unix_socket = os.path.join('/cloudsql', CLOUDSQL_CONNECTION_NAME)

db = MySQLdb.connect(unix_socket=cloudsql_unix_socket,
	user=CLOUDSQL_USER,
	passwd=CLOUDSQL_PASSWORD)

import hashlib
import random

from utils import *
# Create your views here.

@login_required(login_url='/accounts/login/')
def login(request):
	return render(request, 'login.html')

@login_required(login_url='/accounts/signup/')
def signup(request):
	return render(request, 'signup.html')

@csrf_exempt
def makeaccount(request, methods=['POST']):
	#Create a new account from signup page
	data = request.POST
	netid = data.get('email').replace('@princeton.edu', '')
	passw = data.get('passw')
	isd = 0
	if data.get('isdirector') == 'true':
		isd = 1

	#create user's dats in user
	cursor = db.cursor()
	cursor.execute('USE quickcanvass')
	cursor.execute("INSERT INTO user (netid, is_director) VALUES (%s, %s)", (netid, isd))
	cursor.close()
	db.commit()

	#create the instrinsic user in auth_user
	user = User.objects.create_user(netid, netid + '@princeton.edu', passw)
	return redirect('accounts/login')

def about(request):
    return render(request, 'about.html')

def research(request):
    return render(request, 'research.html')

def contact(request):
    return render(request, 'contact.html')

def search(request):
	return render(request, 'search.html')

def volunteercampaigns(request):
	return render(request, 'volunteercampaigns.html')

def volunteerdash(request, netid):
	if not request.user.username == netid:
		return redirect('/accounts/login')
	return render(request, 'volunteerdash.html')

@csrf_exempt
def login_verification(request):
	data = request.POST
	netid = (data.get('email') or "").replace('@princeton.edu', '')
	passw = data.get('passw')

	user = authenticate(username=netid, password=passw)
	if user is not None:
		auth_login(request, user)
		print("authorized")
	else:
	    print("not authed")
	print("Trying to login with " + str(netid) + str(passw))
	return HttpResponse('/volunteerdash/' + user.__dict__['username'])