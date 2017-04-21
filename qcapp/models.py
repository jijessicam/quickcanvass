from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

import os, json
dir_path = os.path.dirname(os.path.realpath(__file__)) + "/static/local_base_data.txt"
with open(dir_path) as data_file:    
    cvass_data = json.load(data_file)
# Create your models here.
class Campaign(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    # members = models.TextField()
    datetime_created = models.DateTimeField(default=timezone.now)
    deadline = models.DateTimeField(null = True)
    contact = models.CharField(max_length = 200, null = True)
    volunteer_ids = models.CharField(max_length = 2500, null = True)
    code = models.CharField(max_length = 8, null = True)
    owner_id = models.IntegerField(null = True)
    survey_id = models.IntegerField(null= True)
    cvass_data = models.TextField(default=cvass_data)
    targetted_years = models.CharField(default="any", max_length=4)

    def publish(self):
        self.save()

    def __str__(self):
        return self.title   # return campaign title 

class Survey(models.Model):
    q1 = models.CharField(max_length=200)
    q2 = models.CharField(max_length=200)
    q3 = models.CharField(max_length=200)
    script = models.CharField(max_length=500)
    owner_id = models.IntegerField(null = True)
    campaign_id = models.IntegerField(null = True)

    def publish(self):
        self.save()

    def __str__(self):
        return self.script[0:50] + "..."   # return campaign title 

class Userdata(models.Model):
	vol_auth_campaign_ids = models.CharField(max_length=80)
	netid = models.CharField(max_length=30)
	is_director = models.IntegerField()
	manager_auth_campaign_id = models.CharField(max_length=20)
	
