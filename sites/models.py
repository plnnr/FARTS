from django.contrib.gis.db import models as geomodels
from django.db import models
from django.contrib.auth.models import User

# steps for clearing data from database:
# delete migration files (if migrations are broken)
# run ./manage.py flush # this deletes data IN the tables
# dm sqlflush | dm dbshell # this DESTROYS the tables themselves
# open pgadmin and manually delete table if required


class BaseZone(models.Model):
    name = models.CharField(max_length = 256, unique=True)

    def __str__(self):
        return self.name

class BaseZoneClass(models.Model):
    name = models.CharField(max_length = 256, unique=True)

    def __str__(self):
        return self.name

DISTRICT_TYPES = (
    (0, 'Historic'),
    (1, 'Conservation'),
    (2, 'Plan'),
)

class District(models.Model):
    type = models.IntegerField(choices=DISTRICT_TYPES)
    name = models.CharField(max_length = 256, unique=True)

    def __str__(self):
        return f'{self.name}: {self.type}'

TRANSFER_PURPOSES = (
    (0, "Tree"),
    (1, "Affordable Housing"),
    (2, "Historic Landmark"),
)

class Site(models.Model):
    class Meta:
        abstract = True # django passes over this model when making migrations unless it's inherited

    # add information that is shared between sending AND receiving sites
    street_address = models.CharField(max_length = 256)
    # multiple_adjacent_sites = models.BooleanField() # does the site have multiple adjacent sites listed together?
    site_size = models.FloatField() # in square feet
    location = geomodels.PointField() # exact XY coordinates
    fuzzy_location = geomodels.PointField() # Location to be displayed to anonymous users
    
    ## Begin zoning 
    # base_zones = models.ManyToManyField(BaseZone, blank=True, related_name='sites')
    # base_zone_classes = models.ManyToManyField(BaseZoneClass, blank=True, related_name='sites')
    # districts = models.ManyToManyField(District, blank=True, related_name='sites')
    base_zones = models.ManyToManyField(BaseZone, blank=True)
    base_zone_classes = models.ManyToManyField(BaseZoneClass, blank=True)
    districts = models.ManyToManyField(District, blank=True)

 
class SendingSite(Site):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sending_sites")
    transfer_purpose = models.IntegerField(choices = TRANSFER_PURPOSES) # Tree, housing, historic landmark
    transferrable_far = models.FloatField()

    def __str__(self):
        return f'{self.street_address}'

class ReceivingSite(Site):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiving_sites")
    target_far = models.FloatField() # desired FAR to receive

    def __str__(self):
        return f'{self.street_address}'
    







# to see all fiels, do `dir(object.object)` for example 
# x = SendingSite.objects.first() # <- first row
# dir(x.location)

class Auction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auction")
    sending_site = models.OneToOneField(SendingSite, on_delete=models.DO_NOTHING)
    # not completed until transaction finalized
    receiving_site = models.OneToOneField(ReceivingSite, on_delete=models.DO_NOTHING)
    reserve_price_sqft = models.IntegerField(default=False) # reserve price per square foot

    def add_bid(self):
        ...
        # check whether sending site is eligible to make bid
        # do other error checking and updating 
    
    def __str__(self):
        return f'Auction for {self.sending_site.street_address} from {user}'