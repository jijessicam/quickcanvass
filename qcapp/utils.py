import hashlib
import string
import json
import MySQLdb
import os, sys
import random

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

def get_college(hallname):
	hallname = hallname.lower()
	if hallname in ['bogle', 'yoseloff', '1976', '1915', '1967', 'emma', 'bloomberg', 'wilf']:
		return 'butler'
	elif hallname in ['addition', 'main']:
		return 'forbes'
	elif hallname in ['blair', 'campbell', 'edwards', 'hamilton', 'joline', 'little']:
		return 'mathey'
	elif hallname in ['buyers', 'campbell', 'holder', 'witherspoon']:
		return 'rocky'
	elif hallname in ['1981', 'wendell', 'fisher', 'hargadon', 'lauritzen', 'baker', 'murley']:
		return 'whitman'
	elif hallname in ['1927', '1937', '1938', '1939', 'dodge', 'feinburg', 'gauss', 'walker', 'wilcox']:
		return 'wilson'

def show_search(json_data, count, values):
	for dat in search(json_data, count, values):
		print(dat)


#Search for json_data for the top count entries that best match the list values
#demand_canvass = n will limit answers to those canvassed no more than n times
def search_rooms(json_data, count, values, demand_canvass):
	#Goals: limit results to best count
	if not any([x in values for x in 'butler', 'forbes', 'mathey', 'rocky', 'whitman', 'wilson']):
		for val in values:
			college = get_college(val)
			if college != None:
				values.append(college)
				break
	#Learn how much everything matches
	to_ret =[]
	for dat in json_data:
		if (dat.get('canvassed', 0) <= demand_canvass):
			dat_values = dat.values()
			rating = 0
			for dat_value in dat_values:
				rating += sum([val.lower() in dat_value.lower() for val in values])
			to_ret.append((dat, rating))
	#Drop those that don't match
	to_ret_pruned = []
	for (dat, rating) in to_ret:
		if rating != 0:
			to_ret_pruned.append((dat, rating))
	to_ret_pruned.sort(key=lambda x: -1 * x[1])
	return to_ret_pruned[0:count]
