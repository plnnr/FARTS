from django.urls import path
from django.shortcuts import render

from . import views

app_name = 'sites'

urlpatterns = [
    path('register/receiving-site', views.receiving_site, name="register-receiving"),
    path('register/sending-site', views.sending_site, name="register-sending"),
    path('search', views.address_search_ajax, name='search'),
    path('get_details', views.get_landuse_details_ajax, name='get_details'),
    path('register/receiving-site/record_receiving_site', views.record_receiving_site, name='record-receiving-site'),
    path('register/sending-site/record_sending_site', views.record_sending_site, name='record-sending-site'),
    path('view/receiving', views.view_receiving, name='view-receiving'),
    path('view/sending', views.view_sending, name='view-sending'),
    path('sending/view', views.view_sending_sites, name='view_sending_sites'),
    path('receiving/view', views.view_receiving_sites, name='view_receiving_sites'),
    path('auction/create', views.create_auction, name='create_auction'),
    path('view/sending/details/<int:id>', views.sending_site_details, name='sending_site_details'),
    path('view/receiving/details/<int:id>', views.receiving_site_details, name='receiving_site_details'),
    path('bid/<int:id>', views.view_auction, name='view_auction'),
]
