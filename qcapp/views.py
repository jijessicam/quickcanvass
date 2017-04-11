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



import hashlib
import random

from utils import *

db = get_db()

# Create your views here.

@login_required(login_url='')
def login(request):
	return render(request, 'login.html')

@login_required(login_url='')
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
	cursor.execute("SELECT (netid) from user where netid=%s and is_director=%s", (netid, isd))
	if cursor.rowcount == 0:
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

#def contact(request):
 #   return render(request, 'contact.html')
def home(request):
	return render(request, 'home.html')

def search(request):
	return render(request, 'search.html')

def volunteercampaigns(request):
	return render(request, 'volunteercampaigns.html')

def editcampaign(request):
	return render(request, 'editcampaign.html')

def managerdash(request, netid):
	if not request.user.username == netid:
		return redirect('/accounts/login')
	if is_user_manager(netid):
		return render(request, 'managerdash.html', {'netid': netid, "isd": 1})
	else:
		return redirect("/volunteerdash/" + netid)

def volunteerdash(request, netid):
	if not request.user.username == netid:
		return redirect('/accounts/login')
	if not is_user_manager(netid):
		return render(request, 'volunteerdash.html', {'netid': netid, "isd": 0})
	else:
		return redirect("/managerdash/" + netid)

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
