from django.contrib.gis import admin
from . import models

admin.site.register(models.SendingSite, admin.OSMGeoAdmin)
admin.site.register(models.ReceivingSite, admin.OSMGeoAdmin)
admin.site.register(models.BaseZone)
admin.site.register(models.BaseZoneClass)
admin.site.register(models.District)
admin.site.register(models.Auction)
admin.site.register(models.Bid)