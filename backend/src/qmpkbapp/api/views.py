# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from qmpkbapp.models import IpAddressInformation

from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.schemas import SchemaGenerator
from rest_framework.permissions import AllowAny
import coreapi,coreschema
from rest_framework.schemas import ManualSchema
from rest_framework_swagger import renderers
import sys,re,os,glob,shutil,subprocess,socket
from django.conf import settings

import requests

from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

def fileApi(request):
	return Response()