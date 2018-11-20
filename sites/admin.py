from django.contrib.gis import admin
from .models import SendingSite

admin.site.register(SendingSite, admin.OSMGeoAdmin)