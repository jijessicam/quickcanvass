import hashlib
import string
import json

def hashit(stri):
    for i in range(0, 500000):
        stri = hashlib.sha224(stri).hexdigest()
    return stri

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