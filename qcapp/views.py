from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.http import JsonResponse
from django import forms
from .forms import CampaignForm
from .forms import SurveyForm
from .models import Campaign
from .models import Survey
from .models import Userdata
import datetime
import os
import pprint as pp
import MySQLdb
from .forms import FillSurveyForm
import django_cas_ng



import hashlib
import random

from utils import *

keys = ['first', 'last', 'dorm', 'college', 'major', 'class', 'id']
princeton_data = get_pton_json_data(keys)

# Create your views here.

def handler404(request):
	response = render_to_response('404.html', {}, context_instance=RequestContext(request))
	response.status_code = 404
	return response

def handler500(request):
	response = render_to_response('500.html', {}, context_instance=RequestContext(request))
	response.status_code = 500
	return response 

def handler403(request):
	response = render_to_response('403.html', {}, context_instance=RequestContext(request))
	response.status_code = 403
	return response 

def logout(request):
	req = django_cas_ng.views.logout(request)
	return redirect('/')

@login_required(login_url='')
def login(request):
	return render(request, 'login.html', {'only_link_to_home': 1})

@login_required(login_url='')
def signup(request):
	return render(request, 'signup.html', {'only_link_to_home': 1})

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
		camp = Campaign.objects.filter(id=idd)
		if camp.count() == 0:
			return JsonResponse({"error": "code does not match any campagn"})
		camp = camp[0]
		camp.volunteer_ids = vol_id
		camp.save()
		userdat = Userdata.objects.filter(id=my_id)[0]
		if userdat.vol_auth_campaign_ids:
			userdat.vol_auth_campaign_ids = (userdat.vol_auth_campaign_ids + "," + str(int(idd)))
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

	#check if user already exists
	userdat = Userdata.objects.filter(netid=netid)
	if not userdat:
		userdat = Userdata(netid=netid, is_director=isd)
		userdat.save()
		#create the userdata
		user = User.objects.create_user(netid, netid + '@princeton.edu', passw)
		user = authenticate(username=netid, password=passw)
		auth_login(request, user)
		return JsonResponse({'error': None ,'url' :'/managerdash/' + netid})
	else:	#user did exist
		return JsonResponse({'error': 'netid already exists' ,'url' :'/signup'})


def about(request):
    return render(request, 'about.html', {"isd": is_user_manager(request.user.username), 'netid': request.user.username, "is_about": 1})

def research(request):
    return render(request, 'research.html')

def home(request):
	return render(request, 'home.html')

@csrf_exempt
def search_by_ids(request):
	if not am_i_authorized(request, camp_id=request.POST.get('campaign_id')):
		# return JsonResponse({'error': "Not Authorized"})
		raise PermissionDenied
	netid = request.user.username
	data = request.POST
	ids = data.get('ids')
	campaign_id = data.get('campaign_id')
	cvass_data = Campaign.objects.filter(id=campaign_id)[0].cvass_data
	results = search_rooms_by_id(princeton_data, cvass_data, ids)
	listed_results = []
	for res in results:
		listed_results.append([res["dorm"], res["first"] + " " + res['last'], "<a href = '/fillsurvey/" + campaign_id + "/" + netid + "/" + str(res["id"])  + "' class='btn ss-button button canvassBtn' >Canvass</a>"])
	if results:
		return JsonResponse({'error': None ,'url' :'/volunteercampaigns', 'results': listed_results}, safe=False)
	else:	# error: room search returned no results 
		return JsonResponse({'error': None ,'url' :'/volunteercampaigns', 'results': []}, safe=False)

@csrf_exempt
def search(request):
	if not am_i_authorized(request, camp_id=request.POST.get('campaign_id')):
		# return JsonResponse({'error': "Not Authorized"})
		raise PermissionDenied
	netid = request.user.username
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
	id_string = ""
	for res in results:
		listed_results.append([res["dorm"], res["first"] + " " + res['last'], "<a style='margin: 0px' href = '/fillsurvey/" + campaign_id + "/" + netid + "/" + str(res["id"])  + "' class='btn ss-button button canvassBtn' >Canvass</a>"])
		id_string = id_string + str(res["id"]) + ","
	udata = Userdata.objects.filter(netid=request.user.username)[0]
	udata.checkout = id_string
	udata.save()
	if results:
		return JsonResponse({'error': None ,'url' :'/volunteercampaigns', 'results': listed_results}, safe=False)
	else:	# error: room search returned no results 
		return JsonResponse({'error': None ,'url' :'/volunteercampaigns', 'results': []}, safe=False)

def volunteercampaigns(request, netid, campaign_id):
	if not am_i_authorized(request, netid=netid, camp_id=campaign_id):
		# return JsonResponse({'error': "Not Authorized"})
		raise PermissionDenied
	camp = Campaign.objects.filter(id=campaign_id)[0]
	title = camp.title
	vol_ids = camp.volunteer_ids.split(",")
	target_years = camp.targetted_years
	if (not request.user.username == netid) or (str(get_my_id(netid)) not in vol_ids):
		return redirect('/accounts/login')
	fillsurveyurl = "/fillsurvey/" + str(campaign_id)+ "/" + str(netid)
	return render(request, 'volunteercampaigns.html',
		{'netid': netid,
		'fillsurvey': fillsurveyurl,
		'title': title,
		'isd': is_user_manager(netid),
		'targetted_years': target_years,
		'checkout': Userdata.objects.filter(netid=request.user.username)[0].checkout})

def fillsurvey(request, netid, campaign_id, voter_id):
	if not am_i_authorized(request, netid=netid, camp_id=campaign_id):
		return JsonResponse({'error': "Not Authorized"})
	json_data = json.load(open(os.path.dirname(os.path.realpath(__file__)) + '/static/princeton_json_data.txt'))
	name = str(json_data[int(voter_id)]["first"] +" "+ json_data[int(voter_id)]["last"])
	dorm = str(json_data[int(voter_id)]["dorm"])
	title = "No title yet"
	count = Campaign.objects.filter(id=campaign_id).count()
	if request.method == "GET":
		if count != 0:
			title = Campaign.objects.filter(id=campaign_id)[0].title
			survey_ID = Campaign.objects.filter(id=campaign_id)[0].survey_id
			script = Survey.objects.filter(campaign_id=campaign_id)[0].script
			q1 = Survey.objects.filter(campaign_id=campaign_id)[0].q1
			q2 = Survey.objects.filter(campaign_id=campaign_id)[0].q2
			q3 = Survey.objects.filter(campaign_id=campaign_id)[0].q3
			data = {"script": script, "q1": q1, "q2": q2, "q3": q3, "name": name, "dorm_number": dorm}
			form = FillSurveyForm()
			form.fields['script'].widget = forms.HiddenInput()
			if q1 == "":
				form.fields['q1'].widget = forms.HiddenInput()
			if q2 == "":
				form.fields['q2'].widget = forms.HiddenInput()
			if q3 == "":
				form.fields['q3'].widget = forms.HiddenInput()
			url_on_cancel = "/volunteercampaigns/" + campaign_id + "/" + str(request.user.username)
			return render(request, 'fillsurvey.html', { 'title': title, 'url_on_cancel': url_on_cancel, 'data': data, 'form': form, 'netid': netid})
	if request.method == "POST":
		form = FillSurveyForm(data=request.POST)
		q1, q2, q3 = "", "", ""
		q1 = request.POST.get('q1', '')
		q2 = request.POST.get('q2', '')
		q3 = request.POST.get('q3', '')
		camp = Campaign.objects.filter(id=campaign_id)[0]
		cvass_data = load_cvass_data(Campaign.objects.filter(id=campaign_id)[0].cvass_data)
		print(voter_id)
		for i, dat in enumerate(cvass_data):
			if str(dat["id"]) == voter_id:
				cvass_data[i]['a1'] = q1
				cvass_data[i]['a2'] = q2
				cvass_data[i]['a3'] = q3
				camp.cvass_data = str(cvass_data)
				camp.save()
				break
		return redirect('/volunteercampaigns/' + campaign_id + '/' + netid)
	
def promote_to_manager(request, netid):
	if not am_i_authorized(request, netid=netid):
		# return JsonResponse({'error': "Not Authorized"})
		raise PermissionDenied
	# Promote volunteer to manager in database 
	isd_new = 1 
	userdat = Userdata.objects.filter(netid=netid)[0]
	userdat.is_director = isd_new
	userdat.save()
	url = "/editcampaign/" + str(netid)
	return redirect(url)

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
			userdat = Userdata.objects.filter(id=owner_id)[0]
			userdat.vol_auth_campaign_ids = userdat.vol_auth_campaign_ids + "," + str(update_id)
			userdat.manager_auth_campaign_id = update_id
			userdat.save()
			code = get_random_code(update_id)
			camps = Campaign.objects.filter(code__isnull=True, id=update_id)
			if camps.count() > 0:
				camp = camps[0]
				camp.code = code
				camp.save()
			return redirect('/managerdash/' + request.user.username)
	if request.method == 'GET':
		count = Campaign.objects.filter(owner_id=owner_id).count()
		form = CampaignForm()
		username = "/managerdash/" + str(request.user.username)
		if count != 0:
			update = Campaign.objects.filter(owner_id=owner_id)[0]
			deadline = update.deadline
			description = update.description
			contact = update.contact
			title = update.title
			data = {"title": title, "contact": contact, "description": description, "deadline": deadline}
			form = CampaignForm(initial = data)
		else:
			return render(request, 'editcampaign.html', {'form': form, 'title': title, 'username': username, 'eliminate_cancel': True, 'isd': 1})
	return render(request, 'editcampaign.html', {'form': form, 'title': title, 'username': username, 'isd': 1, 'netid': netid})

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
	print("test")
	cvass_data = ""
	with open(dir_path) as data_file:    
	    cvass_data = json.load(data_file)
	camp = Campaign.objects.filter(owner_id=owner_id)[0]
	camp.cvass_data = cvass_data
	camp.save()
	return redirect('editsurvey')

@csrf_exempt
def download_survey_data(request):
	owner_id = get_my_id(request.user.username)
	json_data = json.load(open(os.path.dirname(os.path.realpath(__file__)) + '/static/princeton_json_data.txt'))
	surv = Survey.objects.filter(owner_id=owner_id)[0]
	camp = Campaign.objects.filter(owner_id=owner_id)[0]
	cvass_data = load_cvass_data(camp.cvass_data)
	to_ret = [["Script", surv.script, ], ["id", "Name", "Dorm", "College", surv.q1, surv.q2, surv.q3], ]
	for i, dat in enumerate(cvass_data):
		to_ret.append([dat["id"], json_data[i]["first"] + " " + json_data[i]["last"], json_data[i]["dorm"], json_data[i]["college"], dat["a1"], dat["a2"], dat["a3"]])
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
		return render(request, 'editcampaign.html', {'form': form, 'title': 'Before You Create A Survey, Please Create A Campaign.', 'username': request.user.username, 'isd': 1})
	return render(request, 'editsurvey.html', {'form': form, 'title': title, 'username': request.user.username, 'isd': 1, 'netid': netid})


def managerdash(request, netid):
	print(request.user.username, netid)
	if not am_i_authorized(request, netid=netid):
		# return JsonResponse({'error': "Not Authorized"})
		raise PermissionDenied
	campaignid = "No ID yet"
	title = "No Campaign Yet"
	owner_id = get_my_id(request.user.username)
	count = Campaign.objects.filter(owner_id=owner_id).count()
	print("managerdash count was ", count)
	if count != 0:
		title = Campaign.objects.filter(owner_id=owner_id)[0].title
		campaign_code = Campaign.objects.filter(owner_id =owner_id)[0].code
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
		print("HERE I AM AT LINE 440-------------------------")
		user = Userdata.objects.get(id=owner_id)
		campaign_id = getattr(user, "manager_auth_campaign_id")
		print("campaign id: ", campaign_id)
		cvass_data = Campaign.objects.filter(id=campaign_id)[0].cvass_data
		count_dict = count_canvassed_by_res_college(princeton_data, cvass_data)
		print(count_dict)
		campurl = "/editcampaign/" + str(netid)
		survurl = "/editsurvey/" + str(netid)
		return render(request, 'managerdash.html', {'campurl': campurl, 'survurl': survurl,
				'netid': netid, "isd": 1, "campaign_code" : campaign_code,
				"title" : title, "volunteers":  names, "is_managerdash": 1, "num_canvassed": count_dict})
	else:
		return redirect("/volunteerdash/" + netid)

def volunteerdash(request, netid):
	if not am_i_authorized(request, netid=netid):
		# return JsonResponse({'error': "Not Authorized"})
		raise PermissionDenied
	legal_ids = (Userdata.objects.filter(netid=netid)[0].vol_auth_campaign_ids or "").split(",")
	my_campaigns = []
	seen_ids = []
	for idd in legal_ids:
		if idd and idd not in seen_ids:
			camp = Campaign.objects.filter(id=idd)[0]
			my_campaigns.append({'url': '/volunteercampaigns/' + str(idd) + '/' + netid,
									 'title': camp.title,
									 'id': idd})
			seen_ids.append(idd)
	if is_user_manager(netid):
		return render(request, 'volunteerdash.html', {'netid': netid, "isd": 1, "my_campaigns": my_campaigns, "is_volunteerdash": 1})
	else:
		return render(request, 'volunteerdash.html', {'netid': netid, "isd": 0, "my_campaigns": my_campaigns, "is_volunteerdash": 1})

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

