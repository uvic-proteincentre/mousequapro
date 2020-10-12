from rest_framework import routers
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve
from django.views.generic import RedirectView
from django.conf import settings


from .views import fileApi

urlpatterns = [
	url(r'^$',fileApi),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns +=static(settings.FILE_URL,document_root=settings.FILE_ROOT)