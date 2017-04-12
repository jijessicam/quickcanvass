from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.http import JsonResponse
from .forms import CampaignForm
from .models import Campaign
import datetime
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
	#check if user already exists
	cursor = db.cursor()
	cursor.execute('USE quickcanvass')
	cursor.execute("SELECT (netid) from user where netid=%s and is_director=%s", (netid, isd))
	#user did not exist
	if cursor.rowcount == 0:
		cursor.execute("INSERT INTO user (netid, is_director) VALUES (%s, %s)", (netid, isd))
		cursor.close()
		db.commit()

		#create the instrinsic user in auth_user
		user = User.objects.create_user(netid, netid + '@princeton.edu', passw)
		user = authenticate(username=netid, password=passw)
		auth_login(request, user)
		return JsonResponse({'error': None ,'url' :'/managerdash/' + netid})
	else:	#user did exist
		return JsonResponse({'error': 'netid already exists' ,'url' :'/signup'})


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
	if request.method == 'POST':
		form = CampaignForm(data=request.POST)
		if form.is_valid():
			#CampaignInfo.save()
			#process data
			title = request.POST.get('title', '')
			deadline = request.POST.get('deadline', '')
			d= datetime.datetime.strptime(deadline, '%d/%m/%Y')
			deadline = d.strftime('%Y-%m-%d')
			text = request.POST.get('text', '')
			contact = request.POST.get('contact', '')
			updcampaign = Campaign(title = title,
				description = text,
				deadline = deadline,
				contact = contact,
				volunteer_ids= str(get_my_id(request.user.username)) + ",",
				owner_id = get_my_id(request.user.username))
			updcampaign.save()
			return redirect('/managerdash/' + request.user.username)
	if request.method == 'GET':
		form = CampaignForm()
		#args = {}
        #args.update(csrf(request))
        #args['form'] = form
	return render(request, 'editcampaign.html', {'form': form})


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
	my_campaigns = [{'url': 'volunteer/titlea/1/' + netid, 'title': 'titlea', 'id': '1'},
					{'url': 'volunteer/titlea/1/' + netid, 'title': 'titlea', 'id': '2'}]
	if is_user_manager(netid):
		return render(request, 'volunteerdash.html', {'netid': netid, "isd": 1, "my_campaigns": my_campaigns})
	else:
		return render(request, 'volunteerdash.html', {'netid': netid, "isd": 0, "my_campaigns": my_campaigns})

@csrf_exempt
def login_verification(request):
	data = request.POST
	netid = (data.get('email') or "").replace('@princeton.edu', '')
	passw = data.get('passw')

	user = authenticate(username=netid, password=passw)
	if user is not None:
		auth_login(request, user)
		print("authorized")
		return JsonResponse({'url':'/managerdash/' + user.__dict__['username']})
	else:
	    print("not authed")
	    return JsonResponse({'url':'/login/', 'error': 'wrong password'})

