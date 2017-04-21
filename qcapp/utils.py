import hashlib
import string
import json
import MySQLdb
import os, sys
import random
import re
from .models import Userdata

CLOUDSQL_CONNECTION_NAME = 'quickcanvass:us-central1:quickcanvass'
CLOUDSQL_USER = 'root'
CLOUDSQL_PASSWORD = 'cos333'
cloudsql_unix_socket = os.path.join('/cloudsql', CLOUDSQL_CONNECTION_NAME)

def get_random_code(campaign_id):
	have = len(str(campaign_id))
	return ''.join(random.choice(string.digits) for _ in range(8 - have)) + str(campaign_id)

def is_user_manager(netid):
	userdat = Userdata.objects.filter(netid=netid)[0]
	if userdat.is_director:
		return True
	return False

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

def show_search(json_data, count, values):
	for dat in search(json_data, count, values):
		print(dat)

def load_cvass_data(cvass_data_as_str):
	cvass_data_as_str = re.sub(r'u(\'[^\']*\')', r'\1', cvass_data_as_str)
	cvass_data_as_str = cvass_data_as_str.replace("\'", "\"")
	cvass_data_as_json = json.loads(cvass_data_as_str)
	return cvass_data_as_json

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
