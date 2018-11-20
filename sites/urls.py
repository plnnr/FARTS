from django.urls import path
from django.shortcuts import render

from . import views

urlpatterns = [
    path('', views.default_map, name="default"),
    path('search', views.address_search_ajax, name='search'),
    path('get_details', views.get_landuse_details_ajax, name='get_details'),
]
