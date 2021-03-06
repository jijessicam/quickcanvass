import hashlib
import string
import json
import MySQLdb
import os, sys
import random
import re
from .models import Userdata
from .models import Campaign
from .models import Survey

CLOUDSQL_CONNECTION_NAME = 'quickcanvass:us-central1:quickcanvass'
CLOUDSQL_USER = 'root'
CLOUDSQL_PASSWORD = 'cos333'
cloudsql_unix_socket = os.path.join('/cloudsql', CLOUDSQL_CONNECTION_NAME)

#Wrapper function to determine if a user is allowed to see a certain page
def am_i_authorized(request, netid=None, camp_id=None, surv_id=None, manager_req=False):
	ans = am_i_authorized_inner(request, netid, camp_id, surv_id, manager_req)
	print("(Netid Check, Campaign Check, Survey Check", ans)
	return all(ans)

#Helper function to determine if a user is allowed to see a certain page
def am_i_authorized_inner(request, netid_goal=None, camp_id=None, surv_id=None, manager_req=False):
	if netid_goal and not request.user.username == netid_goal:
		return (False, False, False)
	my_id = str(get_my_id(request.user.username))
	if manager_req:
		camp_good = True
		if camp_id:
			camp_good = (my_id == Campaign.objects.filter(id=camp_id).owner_id)
		surv_good = True
		if surv_id:
			surv_good = (my_id == Survey.objects.filter(id=surv_id).owner_id)
		return (True, camp_good, surv_good)
	else:
		camp_good = True
		if camp_id:
			camp_good = (my_id in (Campaign.objects.filter(id=camp_id)[0].volunteer_ids).split(","))
		surv_good = True
		if surv_id:
			camp_id_of_surv == Survey.objects.filter(id=surv_id).campaign_id
			surv_good = (my_id in (Campaign.objects.filter(id=camp_id_of_surv)[0].volunteer_ids).split(","))
		return (True, camp_good, surv_good)

	
	legal_manager = Campaign

#Get the code corresponding to this campaign id
def get_code(campaign_id):
	random.seed(campaign_id)
	return str(random.random())[2:10]

#Is this user a manager?
def is_user_manager(netid):
	userdat = Userdata.objects.filter(netid=netid)[0]
	if userdat.is_director:
		return True
	return False

#What's my numerical id?
def get_my_id(netid):
	userdat = Userdata.objects.filter(netid=netid)[0]
	return userdat.id

#Return a list of dicts with the list flist as keys
#example: first_last = get_pton_json_data(['first', 'last'])
#first_last[0] will be {'first': 'Seraina', 'last': 'Steiger'}
def get_pton_json_data(flist=None):
	data = json.load(open(os.path.dirname(os.path.realpath(__file__)) + '/static/princeton_json_data.txt'))
	if not flist:
		return data
	new_data = []
	for dat in data:
		new_data.append({key: dat[key] for key in flist})
	return new_data

#Parse the loaded canvassing data
def load_cvass_data(cvass_data_as_str):
	cvass_data_as_str = re.sub(r'u(\'[^\']*\')', r'\1', cvass_data_as_str)
	cvass_data_as_str = cvass_data_as_str.replace("\'", "\"")
	cvass_data_as_json = json.loads(cvass_data_as_str)
	return cvass_data_as_json

#Capitalize a word
def cap(string):
	if not string:
		return ""
	return string[0].upper() + string[1:]

#Count how many people in each res college were canvassed during this campaign
def count_canvassed_by_res_college(json_data, cvass_data):
	cvass_data = load_cvass_data(cvass_data)
	res_colleges = {}
	for i in range(0, len(json_data)):
		college = cap(json_data[i]['college'])
		if college in res_colleges.keys():
			res_colleges[college] = (res_colleges[college][0], res_colleges[college][1] + 1)
		else:
			res_colleges[college] = (0, 1)
		if cvass_data[i]['a1']:
			res_colleges[college] = (res_colleges[college][0] + 1, res_colleges[college][1])
	return res_colleges

#Search function used on volunteercampaigns page
def search_rooms(json_data, cvass_data, count, res_college, floor, hallway, abbse, year):
	to_ret = []
	cvass_data = load_cvass_data(cvass_data)
	for i, dat in enumerate(json_data):
		if not cvass_data[i]["a1"]:
			was_good = True
			stripped_dorm = [x for x in dat["dorm"] if x in "1234567890"]
			if (dat["college"].lower() != res_college.lower()):
				continue
			if (floor != "any" and len(stripped_dorm) > 0 and stripped_dorm[0] != floor) or stripped_dorm == "":
				continue
			if hallway != "any" and hallway not in dat["dorm"].lower():
				continue
			if abbse != "AB/BSE" and abbse not in dat["major"]:
				continue
			if year != "any" and year not in dat["class"]:
				continue
			to_ret.append(dat)
	to_ret.sort(key=lambda x: x["dorm"])
	if count == "every":
		return to_ret
	return to_ret[0:int(count)]

#Which voters match these id numbers?
#Used to display saved search results
def search_rooms_by_id(json_data, cvass_data, ids):
	ids = ids.split(",")
	to_ret = []
	cvass_data = load_cvass_data(cvass_data)
	for i, dat in enumerate(json_data):
		if not cvass_data[i]["a1"]:
			if str(dat["id"]) in ids:
				to_ret.append(dat)
	to_ret.sort(key=lambda x: x["dorm"])
	return to_ret
