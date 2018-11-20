from django.contrib.gis.db import models as geomodels
from django.db import models
from django.contrib.auth.models import User

# steps for clearing data from database:
# delete migration files (if migrations are broken)
# run ./manage.py flush
 
class SendingSite(models.Model):
    street_address = models.CharField(max_length = 256)
    multiple_adjacent_sites = models.BooleanField() # does the site have multiple adjacent sites listed together?
    site_size = models.FloatField() # in square feet
    location = geomodels.PointField() # exact XY coordinates
    fuzzy_location = geomodels.PointField() # Location to be displayed to anonymous users
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sending_sites")
    transfer_purpose = models.CharField(max_length = 256) # Tree, housing, historic landmark
    ## Begin zoning 
    base_zone = models.CharField(max_length = 256)
    base_zone_class = models.CharField(max_length = 256) # MDZ / MUZ

    plan_district = models.CharField(max_length = 256)
    conservation_district = models.CharField(max_length = 256)

    historic_district = models.BooleanField(default=False)
    #in_a_overlay = models.BooleanField(default=False)
    #in_b_overlay = models.BooleanField(default=False)
    #in_c_overlay = models.BooleanField(default=False)
    # ... continue for all overlay zones ...

    def __str__(self):
        return f'{self.base_zone_class}: {self.street_address}'

# class ReceivingSite(models.Model):
#     street_address = models.CharField(max_length = 256) # should be optional since not all receiving sites will have an address yet

    


# class Zone(models.Model):
#     name = models.CharField(max_length = 256)

# class Overlay(models.Model):
#     name = models.CharField(max_length = 256)





# to see all fiels, do `dir(object.object)` for example 
# x = SendingSite.objects.first() # <- first row
# dir(x.location)