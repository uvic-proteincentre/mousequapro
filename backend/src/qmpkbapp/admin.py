# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from .models import IpAddressInformation
class IpAddressInformationAdmin(admin.ModelAdmin):
	"""docstring for ClassName"""
	list_display=["__unicode__","access_date"]
	class Meta:
		model=IpAddressInformation

admin.site.register(IpAddressInformation,IpAddressInformationAdmin)