import hashlib
import string
import json
import MySQLdb
import os, sys
import random
import re

CLOUDSQL_CONNECTION_NAME = 'quickcanvass:us-central1:quickcanvass'
CLOUDSQL_USER = 'root'
CLOUDSQL_PASSWORD = 'cos333'
cloudsql_unix_socket = os.path.join('/cloudsql', CLOUDSQL_CONNECTION_NAME)

def get_random_code(campaign_id):
	have = len(str(campaign_id))
	return ''.join(random.choice(string.digits) for _ in range(8 - have)) + str(campaign_id)

def get_db():
	db = MySQLdb.connect(unix_socket=cloudsql_unix_socket,
	user=CLOUDSQL_USER,
	passwd=CLOUDSQL_PASSWORD)
	return db

def is_user_manager(netid):
	db = get_db()
	cursor = db.cursor()
	cursor.execute('USE quickcanvass')
	cursor.execute('SELECT is_director from user where netid=%s', (netid, ))
	for row in cursor:
		if row[0] == 1:
			return True
		else:
			return False

def get_my_id(netid):
	db = get_db()
	cursor = db.cursor()
	cursor.execute('USE quickcanvass')
	cursor.execute('SELECT id from user where netid=%s', (netid, ))
	for row in cursor:
		return int(row[0])


#not sure what this will take as input yet
#maybe also just upload the thing
def get_create_campaign_sql():
	title = ''
	description = ''
	volnteer_ids = ''
	code = ''
	owner_id = ''
	#no need to store in-common data across each user
	#just netid and the data collected by campaign
	cvass_data = str(get_pton_json_data(['email']))
	return "INSERT INTO campaign (title, description, volunteer_ids, code, owner_id, cvass_data) VALUES (%s, %s, %s, %s)", (title, description, volunteer_ids, code, owner_id, cvass_data)


#Return a list of dicts with the list flist as keys
#example: first_last = get_pton_json_data(['first', 'last'])
#first_last[0] will be {'first': 'Seraina', 'last': 'Steiger'}
def get_pton_json_data(flist=None):
	data = json.load(open('qcapp/static/princeton_json_data.txt'))
	if not flist:
		return data
	new_data = []
	for dat in data:
		new_data.append({key: dat[key] for key in flist})
	return new_data

def show_search(json_data, count, values):
	for dat in search(json_data, count, values):
		print(dat)

def search_rooms(json_data, cvass_data, count, res_college, floor, hallway, abbse, year):
	to_ret = []
	cvass_data = re.sub(r'u(\'[^\']*\')', r'\1', cvass_data)
	cvass_data = cvass_data.replace("\'", "\"")
	cvass_data = json.loads(cvass_data)
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
