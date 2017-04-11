import hashlib
import string
import json
import MySQLdb
import os, sys

CLOUDSQL_CONNECTION_NAME = 'quickcanvass:us-central1:quickcanvass'
CLOUDSQL_USER = 'root'
CLOUDSQL_PASSWORD = 'cos333'
cloudsql_unix_socket = os.path.join('/cloudsql', CLOUDSQL_CONNECTION_NAME)

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