from django.urls import path
from django.shortcuts import render

from . import views

app_name = 'sites'

urlpatterns = [
    path('register/receiving-site', views.receiving_site, name="register-receiving"),
    path('register/sending-site', views.sending_site, name="register-sending"),
    path('search', views.address_search_ajax, name='search'),
    path('get_details', views.get_landuse_details_ajax, name='get_details'),
]
