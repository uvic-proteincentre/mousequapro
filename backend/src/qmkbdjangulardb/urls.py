"""qmkbdjangulardb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view
from qmpkbapp.views import basicSearch,advancedSearch,concentration,assaydetails,protVista,\
SwaggerRestAPIView,goterm,pathway,peptideUniqueness,pathwayview,contact,geneExp,foldChange,\
detailInformation,detailConcentration,saveFastaFile,submission,generateDownload

# from django.contrib.auth.decorators import login_required
# import django_cas_ng.views


schema_view= get_swagger_view(title="Rest API Documents")

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^resultsapi/$', basicSearch, name='result'),
    url(r'^advanceresultsapi/$', advancedSearch, name='advanceresult'),
    url(r'^seqfeaturesapi/$', protVista, name='seqfeatures'),
    url(r'^concentrationapi/$', concentration, name='concentration'),
    url(r'^assaydetailsapi/$', assaydetails, name='assaydetails'),
    url(r'^gotermapi/$', goterm, name='goterm'),
    url(r'^geneexpapi/$', geneExp, name='geneexp'),
    url(r'^pathwayapi/$', pathway, name='pathway'),
    url(r'^pathwayviewapi/$', pathwayview, name='pathwayview'),
    url(r'^peptideuniquenessapi/$', peptideUniqueness, name='peptideUniqueness'),
    url(r'^restapi/$', SwaggerRestAPIView.as_view()),
    url(r'^docapi/', schema_view),
    url(r'^fileapi/', include('qmpkbapp.api.urls')),
    url(r'^contactapi/$', contact, name='contact'),
    url(r'^foldChangeapi/$', foldChange, name='foldChange'),
    url(r'^detailinformationapi/$', detailInformation, name='detailinformation'),
    url(r'^detailConcentrationapi/$', detailConcentration, name='detailconcentration'),
    url(r'^fastafileapi/$', saveFastaFile, name='savefastafile'),
    url(r'^submissionapi/$', submission, name='submission'),
    url(r'^downloadapi/$', generateDownload, name='generateDownload'),
    #after login removed delete or intacivte remining url and active the inactive url
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^.*',TemplateView.as_view(template_name="qmpkb_home.html"), name='home'),
    # url(r'^.*',login_required(TemplateView.as_view(template_name="qmpkb_home.html")), name='home'),
    # url(r'^accounts/login/$',cas_views.login, name='cas_ng_login'),
    # url(r'^accounts/login/$',cas_views.logout, name='cas_ng_logout'),
    # url(r'^accounts/login/$*',cas_views.callback, name='cas_ng_proxy_callback'),

]