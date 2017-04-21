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
from .forms import SurveyForm
from .models import Campaign
from .models import Survey
from .models import Userdata
import datetime
import os
import pprint as pp
import MySQLdb



import hashlib
import random

from utils import *

keys = ['first', 'last', 'dorm', 'college', 'major', 'class']
princeton_data = get_pton_json_data(keys)

# Create your views here.

#@login_required(login_url='')
def login(request):
	return render(request, 'login.html')

#@login_required(login_url='')
def signup(request):
	return render(request, 'signup.html')

@csrf_exempt
def join_new_campaign(request, methods=['POST']):
	data = request.POST
	code = data.get('code')
	print(code)
	camp = Campaign.objects.filter(code=code)[0]
	ids_and_vol_ids = [(camp.id, camp.volunteer_ids), ]
	my_id = str(get_my_id(request.user.username))
	for (idd, vol_id) in ids_and_vol_ids:
		vol_id = vol_id + my_id + ","
		camp = Campaign.objects.filter(id=idd)[0]
		camp.volunteer_ids = vol_id
		camp.save()
		userdat = Userdata.objects.filter(id=my_id)[0]
		if userdat.vol_auth_campaign_ids:
			userdat.vol_auth_campaign_ids = (userdat.vol_auth_campaign_id + "," + str(int(idd)))
		else:
			userdat.vol_auth_campaign_ids = str(int(idd))
		userdat.save()
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
	userdat = Userdata.objects.filter(netid=netid)
	if not userdat:
		userdat = Userdata(netid=netid, is_director=isd)
		userdat.save()
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
	campaign_id = data.get('campaign_id')
	cvass_data = Campaign.objects.filter(id=campaign_id)[0].cvass_data
	results = search_rooms(princeton_data, cvass_data, count, res_college, floor, hallway, abbse, year)
	listed_results = []
	for res in results:
		listed_results.append([res["dorm"], res["first"], res["last"], res["major"], res["class"]])
	if results: 
		return JsonResponse({'error': None ,'url' :'/volunteercampaigns', 'results': listed_results}, safe=False)
	else:	# error: room search returned no results 
		return JsonResponse({'error': 'room search failed' ,'url' :'/volunteercampaigns'})

def volunteercampaigns(request, netid, campaign_id):
	camp = Campaign.objects.filter(id=campaign_id)[0]
	title = camp.title
	vol_ids = camp.volunteer_ids.split(",")
	target_years = camp.targetted_years
	if (not request.user.username == netid) or (str(get_my_id(netid)) not in vol_ids):
		return redirect('/accounts/login')
	fillsurveyurl = "/fillsurvey/" + str(campaign_id)+ "/" + str(netid)
	return render(request, 'volunteercampaigns.html', {'netid': netid, 'fillsurvey': fillsurveyurl, 'title': title, 'isd': is_user_manager(netid), 'targetted_years': target_years})

def fillsurvey(request, netid, campaign_id):
	title = "No title yet"
	count = Campaign.objects.filter(code=campaign_id).count()
	if count != 0:
		title = Campaign.objects.filter(code=campaign_id)[0].title
	username = "/volunteerdash/" + str(request.user.username)
	return render(request, 'fillsurvey.html', { 'title': title, 'username': username})

def promote_to_manager(request, netid):
	# Promote volunteer to manager in database 
	isd_new = 1 
	userdat = Userdata.objects.filter(netid=netid)[0]
	userdat.is_director = isd_new
	userdat.save()
	# Redirect to edit-campaign so they can set up their campaign
	string = "/editcampaign/" + str(netid)
	return redirect(string)

def editcampaign(request, netid):
	if not is_user_manager(netid):
		return redirect('/accounts/login')
	if not request.user.username == netid:
		return redirect('/accounts/login')
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
			if count == 0:
				updcampaign = Campaign(title = title,
					description = description,
					deadline = deadline,
					contact = contact,
					targetted_years = targetted_years,
					volunteer_ids= str(get_my_id(request.user.username)) + ",",
					owner_id = owner_id)
				updcampaign.save()
				campaign_id = (Campaign.objects.filter(owner_id=owner_id)[0]).id
				survey = Survey(
					q1 = "[Sample question]  Are you supporting Michelle Obama in the upcoming USG election?",
					q2 = "[Sample question]  What issues are most important to you?",
					q3 = "",
					script = "[This script is read to each voter by your volunteer.]  Hello, I'm Michelle and I'm running for USG because...",
					owner_id = owner_id,
					campaign_id = campaign_id)
				survey.save()
			update_id = Campaign.objects.filter(owner_id=owner_id)[0].id
			#eventuall make this additive instead of overriding
			userdat = Userdata.objects.filter(id=owner_id)[0]
			userdat.vol_auth_campaign_ids = update_id
			userdat.manager_auth_campaign_id = update_id
			userdat.save()
			code = get_random_code(update_id)
			camps = Campaign.objects.filter(code__isnull=True, id=update_id)
			if camps.count() > 0:
				print("inner")
				camp = camps[0]
				camp.code = code
				camp.save()
			print("saved")
			print(code, update_id, camps.count())	
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


@csrf_exempt
def clear_survey_data(request):
	owner_id = get_my_id(request.user.username)
	surv = Survey.objects.filter(owner_id=owner_id)[0]
	surv.q1 = "[Sample question]  Are you supporting Michelle Obama in the upcoming USG election?"
	surv.q2 = "[Sample question]  What issues are most important to you?"
	surv.q3 = ""
	surv.script = "[This script is read to each voter by your volunteer.]  Hello, I'm Michelle and I'm running for USG because..."
	surv.save()
	dir_path = os.path.dirname(os.path.realpath(__file__)) + "/static/local_base_data.txt"

	cvass_data = ""
	with open(dir_path) as data_file:    
	    cvass_data = json.load(data_file)
	camp = Campaign.objects.filter(owner_id=owner_id)[0]
	camp.cvass_data = cvass_data
	camp.save()
	return JsonResponse({"error": None})

@csrf_exempt
def download_survey_data(request):
	owner_id = get_my_id(request.user.username)
	json_data = load_cvass_data()
	surv = Survey.objects.filter(owner_id=owner_id)[0]
	camp = Campaign.objects.filter(owner_id=owner_id)[0]
	cvass_data = load_cvass_data(camp.cvass_data)
	to_ret = [["Script", surv.script, ], ["id", "Name", "Dorm", "College", surv.q1, surv.q2, surv.q3], ]
	for i, dat in enumerate(cvass_data):
		to_ret.append([dat["id"], json_data[i]["first"] + json_data[i]["last"], json_data[i]["dorm"], json_data[i]["college"], dat["a1"], dat["a2"], dat["a3"]])
	return JsonResponse(to_ret, safe=False)

def editsurvey(request):
	title = "No Campaign Yet"
	owner_id = get_my_id(request.user.username)
	count = Campaign.objects.filter(owner_id=owner_id).count()
	if count != 0:
		title = Campaign.objects.filter(owner_id=owner_id)[0].title
		survey = Survey.objects.filter(owner_id=owner_id)[0]
	print(title)
	print(survey.q1)

	if request.method == 'POST':
		form = SurveyForm(data=request.POST)
		if form.is_valid():
			#CampaignInfo.save()
			#process data
			script = request.POST.get('script', '')
			q1 = request.POST.get('q1', '')
			q2 = request.POST.get('q2')
			q3 = request.POST.get('q3', '')
			owner_id = get_my_id(request.user.username)
			count = Survey.objects.filter(owner_id=owner_id).count()
			if count != 0:
				update = Survey.objects.filter(owner_id=owner_id)[0]
				update.script = script
				update.q1 = q1
				update.q2 = q2
				update.q3 = q3
				update.owner_id = owner_id
				update.save()
			if count == 0:
				updcampaign = Survey(script = script,
					q1 = q1,
					q2 = q2,
					q3 = q3,
					owner_id = owner_id)
				updcampaign.save()
		return redirect("/volunteerdash/" + str(request.user.username))
	if request.method == 'GET':
		count = Survey.objects.filter(owner_id=owner_id).count()
		form = SurveyForm()
		if count != 0:
			update = Survey.objects.filter(owner_id=owner_id)[0]
			script = update.script
			q1 = update.q1
			q2 = update.q2
			q3 = update.q3

			data = {"script": script, "q1": q1, "q2": q2, "q3": q3}
			form = SurveyForm(initial = data)

	username = "/managerdash/"
	# not fixed here...
	if title == "No Campaign Yet":
		form = CampaignForm()
		## fix this so its more redirect-y/also that it updates database -- so you can't just type the URL in
		## -- like, check if manager, if not manager, return to volunteer dash
		## also fix this so its not "if title == "No Campaign Yet"
	#	return redirect("/volunteerdash/" + netid)
		return render(request, 'editcampaign.html', {'form': form, 'title': 'Before You Create A Survey, Please Create A Campaign.', 'username': request.user.username})
	return render(request, 'editsurvey.html', {'form': form, 'title': title, 'username': request.user.username})


def managerdash(request, netid):
	campaignid = "No ID yet"
	title = "No Campaign Yet"
	owner_id = get_my_id(request.user.username)
	count = Campaign.objects.filter(owner_id=owner_id).count()
	print("managerdash count was ", count)
	if count != 0:
		title = Campaign.objects.filter(owner_id=owner_id)[0].title
		campaign_code = Campaign.objects.filter(owner_id =owner_id)[0].code
	#print("managerdash code was ", campaign_code)
	# if no campaign associated with username,
	if not request.user.username == netid:
		return redirect('/accounts/login')
	if is_user_manager(netid):
		if count == 0:
			return editcampaign(request, netid)
		volunteers = list(set(Campaign.objects.filter(owner_id =owner_id)[0].volunteer_ids.split(",")))
		names = []
		for each in volunteers:
			if each:
				names.append(Userdata.objects.filter(id=each)[0].netid)
		campurl = "/editcampaign/" + str(netid)
		survurl = "/editsurvey/" + str(netid)
		return render(request, 'managerdash.html', {'campurl': campurl, 'survurl': survurl,
				'netid': netid, "isd": 1, "campaign_code" : campaign_code,
				"title" : title, "volunteers":  names})
	else:
		return redirect("/volunteerdash/" + netid)

def volunteerdash(request, netid):
	if not request.user.username == netid:
		return redirect('/accounts/login')
	legal_ids = (Userdata.objects.filter(netid=netid)[0].vol_auth_campaign_ids or "").split(",")
	my_campaigns = []
	seen_ids = []
	for idd in legal_ids:
		if idd not in seen_ids:
			camp = Campaign.objects.filter(id=idd)[0]
			my_campaigns.append({'url': '/volunteercampaigns/' + str(idd) + '/' + netid,
									 'title': camp.title,
									 'id': idd})
			seen_ids.append(idd)
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

