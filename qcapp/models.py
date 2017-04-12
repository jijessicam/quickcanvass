from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

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
    cvass_data = models.TextField(default="some json data")

    def publish(self):
        self.save()

    def __str__(self):
        return self.title   # return campaign title 
