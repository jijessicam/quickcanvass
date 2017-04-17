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
import pprint as pp
import MySQLdb



import hashlib
import random

from utils import *

db = get_db()

keys = ['first', 'last', 'dorm', 'college', 'major', 'class']
princeton_data = get_pton_json_data(keys)

# Create your views here.

@login_required(login_url='')
def login(request):
	return render(request, 'login.html')

@login_required(login_url='')
def signup(request):
	return render(request, 'signup.html')

@csrf_exempt
def join_new_campaign(request, methods=['POST']):
	data = request.POST
	code = data.get('code')
	print(code)
	cursor = db.cursor()
	cursor.execute("USE quickcanvass")
	cursor.execute("SELECT id, volunteer_ids from qcapp_campaign where code=%s", (code, ))
	ids_and_vol_ids = []
	for row in cursor:
		print(row)
		ids_and_vol_ids.append((row[0], row[1]))
	my_id = str(get_my_id(request.user.username))
	for (idd, vol_id) in ids_and_vol_ids:
		vol_id = vol_id + my_id + ","
		cursor.execute("UPDATE qcapp_campaign SET volunteer_ids=%s where id=%s", (vol_id, idd))
		db.commit()
		cursor.execute("SELECT vol_auth_campaign_ids from user where id=%s", (my_id, ))
		for row in cursor:
			cursor.execute("UPDATE user SET vol_auth_campaign_ids=%s where id=%s", (row[0] + "," + str(int(idd)), my_id))
			db.commit()
	return JsonResponse({'error': None })


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

@csrf_exempt
def search(request):
	data = request.POST
	res_college = data.get('res_college')
	floor = data.get('floor')
	hallway = data.get('hallway')
	abbse = data.get('abbse')
	year = data.get('year')
	count = data.get('count')
	# list of room results
	results = search_rooms(princeton_data, count, res_college, floor, hallway, abbse, year)
	listed_results = []
	for res in results:
		listed_results.append([res["dorm"], res["first"], res["last"], res["major"], res["class"]])
	print(listed_results)
	if results: 
		return JsonResponse({'error': None ,'url' :'/volunteercampaigns', 'results': listed_results}, safe=False)
	else:	# error: room search returned no results 
		return JsonResponse({'error': 'room search failed' ,'url' :'/volunteercampaigns'})

def volunteercampaigns(request, netid, campaign_id):
	cursor = db.cursor()
	cursor.execute('USE quickcanvass')
	cursor.execute('SELECT title, volunteer_ids, targetted_years from qcapp_campaign where id=%s', (campaign_id, ))
	for row in cursor:
		title = row[0]
		vol_ids = row[1].split(",")
	if (not request.user.username == netid) or (str(get_my_id(netid)) not in vol_ids):
		return redirect('/accounts/login')
	return render(request, 'volunteercampaigns.html', {'netid': netid, 'title': title, 'isd': is_user_manager(netid), 'targetted_years': row[2]})

def editcampaign(request):
	title = "No Campaign Yet"
	owner_id = get_my_id(request.user.username)
	count = Campaign.objects.filter(owner_id=owner_id).count()
	if count != 0:
		title = Campaign.objects.filter(owner_id=owner_id)[0].title

	if request.method == 'POST':
		form = CampaignForm(data=request.POST)
		if form.is_valid():
			#CampaignInfo.save()
			#process data
			targetted_years = request.POST.get('targetted_years', '')
			title = request.POST.get('title', '')
			deadline = form.cleaned_data.get('deadline')
			description = request.POST.get('description', '')
			contact = request.POST.get('contact', '')
			owner_id = get_my_id(request.user.username)
			count = Campaign.objects.filter(owner_id=owner_id).count()
			if count != 0:
				update = Campaign.objects.filter(owner_id=owner_id)[0]
				update.targetted_years = targetted_years
				update.deadline = deadline
				update.description = description
				update.contact = contact
				update.title = title
				update.owner_id = owner_id
				update.save()
				db.commit()
			if count == 0:
				updcampaign = Campaign(title = title,
					description = description,
					deadline = deadline,
					contact = contact,
					targetted_years = targetted_years,
					volunteer_ids= str(get_my_id(request.user.username)) + ",",
					owner_id = owner_id)
				updcampaign.save()
				db.commit()
			cursor = db.cursor()
			cursor.execute("USE quickcanvass")
			cursor.execute("SELECT id from qcapp_campaign where owner_id=%s", (owner_id, ))
			update_ids = []
			for row in cursor:
				update_ids.append(row[0])
			for update_id in update_ids:
				#eventuall make this additive instead of overriding
				cursor.execute("UPDATE user SET vol_auth_campaign_ids=%s, manager_auth_campaign_id=%s WHERE id=%s", (update_id, update_id, owner_id))
				db.commit()
			code = get_random_code(update_ids[0])
			cursor.execute("UPDATE qcapp_campaign SET code=%s where id=%s and code IS NULL", (code, update_ids[0]))
			db.commit()
			cursor.close()
			return redirect('/managerdash/' + request.user.username)
	if request.method == 'GET':
		count = Campaign.objects.filter(owner_id=owner_id).count()
		form = CampaignForm()
		if count != 0:
			update = Campaign.objects.filter(owner_id=owner_id)[0]
			deadline = update.deadline
			description = update.description
			contact = update.contact
			title = update.title
			data = {"title": title, "contact": contact, "description": description, "deadline": deadline}
			form = CampaignForm(initial = data)
	username = "/managerdash/" + str(request.user.username)
	return render(request, 'editcampaign.html', {'form': form, 'title': title, 'username': username})

def editsurvey(request):
	return render(request, 'editsurvey.html')


def managerdash(request, netid):
	campaignid = "No ID yet"
	title = "No Campaign Yet"
	owner_id = get_my_id(request.user.username)
	count = Campaign.objects.filter(owner_id=owner_id).count()
	if count != 0:
		title = Campaign.objects.filter(owner_id=owner_id)[0].title
		campaign_code = Campaign.objects.filter(owner_id =owner_id)[0].code
	# if no campaign associated with username,
	if not request.user.username == netid:
		return redirect('/accounts/login')
	if is_user_manager(netid):
		if count == 0:
			return editcampaign(request)
		volunteers = Campaign.objects.filter(owner_id =owner_id)[0].volunteer_ids.split(",")
		names = []
		cursor = db.cursor()
		cursor.execute("USE quickcanvass")
		for each in volunteers:
			cursor.execute("SELECT netid from user where id=%s", (each, ))
			for row in cursor:
				names.append(row[0])

		return render(request, 'managerdash.html', {'netid': netid, "isd": 1, "campaign_code" : campaign_code, "title" : title, "volunteers":  names})
	else:
		return redirect("/volunteerdash/" + netid)

def volunteerdash(request, netid):
	if not request.user.username == netid:
		return redirect('/accounts/login')
	cursor = db.cursor()
	cursor.execute('USE quickcanvass')
	cursor.execute('SELECT vol_auth_campaign_ids from user where netid=%s', (netid, ))
	for row in cursor:
		legal_ids = (row[0] or "").split(",")
	my_campaigns = []
	for idd in legal_ids:
		cursor.execute("SELECT title, targetted_years from qcapp_campaign where id=%s", (idd, ))
		for row in cursor:
			my_campaigns.append({'url': '/volunteercampaigns/' + str(idd) + '/' + netid,
								 'title': row[0],
								 'id': idd})
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

