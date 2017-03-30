from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

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

#@login_required(login_url='login')
def login(request):
	return render(request, 'login.html')

#@login_required(login_url='login')
def signup(request):
	return render(request, 'signup.html')

@csrf_exempt
def makeaccount(request, methods=['POST']):
	#wow here's where we acutally upload the stuff to the db
	data = request.POST
	print("test", data.get('email'), data.get('passw'), data.get('isdirector'))
	#create a random 16 character salt for passwords
	salt = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
	hashed_pass = hashit(data.get('passw') + salt)
	cursor = db.cursor()
	cursor.execute('USE quickcanvass')
	cursor.execute('SELECT * FROM princeton')
	for row in cursor:
		print row
	print(hashed_pass)
	return redirect('/login')

def about(request):
    return render(request, 'about.html')

def research(request):
    return render(request, 'research.html')

def contact(request):
    return render(request, 'contact.html')

def search(request):
	return render(request, 'search.html')

def volunteerdash(request):
	return render(request, 'volunteerdash.html')