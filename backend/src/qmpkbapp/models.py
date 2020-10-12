# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.db import models

# Create your models here.

class IpAddressInformation(models.Model):
	ip_address=models.CharField(max_length=1200,blank=False)
	access_date=models.DateTimeField(auto_now_add=True,auto_now=False)
	def __unicode__(self):
		return self.ip_address