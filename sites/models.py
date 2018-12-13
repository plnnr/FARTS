from django.contrib.gis.db import models as geomodels
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.utils import timezone

# steps for clearing data from database:
# delete migration files (if migrations are broken)
# run ./manage.py flush # this deletes data IN the tables
# dm sqlflush | dm dbshell # this DESTROYS the tables themselves
# open pgadmin and manually delete table if required

cityhall = """{
    "type": "Polygon",
    "coordinates": [
        [
        [
            -122.67877619078355,
            45.51477893629183
        ],
        [
            -122.67884560270724,
            45.51465077686185
        ],
        [
            -122.67921018576193,
            45.514748371001176
        ],
        [
            -122.67957476342676,
            45.514845964341774
        ],
        [
            -122.67950535779129,
            45.5149741214388
        ],
        [
            -122.6794359485625,
            45.51510228076183
        ],
        [
            -122.6793665411304,
            45.51523043790462
        ],
        [
            -122.67929713100335,
            45.51535859727345
        ],
        [
            -122.67893254255877,
            45.51526100041557
        ],
        [
            -122.67856795591081,
            45.515163402759
        ],
        [
            -122.67863736873282,
            45.51503525427614
        ],
        [
            -122.67870677975819,
            45.5149070954299
        ],
        [
            -122.67877619078355,
            45.51477893629183
        ]
        ]
    ]
}"""

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
    (3, "Other"),
)

class Site(models.Model):
    class Meta:
        abstract = True # django passes over this model when making migrations unless it's inherited

    street_address = models.CharField(max_length = 256)
    site_size = models.FloatField() # in square feet
    building_size = models.FloatField()
    site_far = models.FloatField()
    location = geomodels.PointField() # exact XY coordinates
    fuzzy_location = geomodels.PointField() # Location to be displayed to anonymous users
    parcel_poly = geomodels.PolygonField(default = cityhall)
    pmaps_object = JSONField()
    created = models.DateTimeField(auto_now_add=True)

    ## Begin zoning 
    base_zones = models.ManyToManyField(BaseZone, blank=True)
    base_zone_classes = models.ManyToManyField(BaseZoneClass, blank=True)
    districts = models.ManyToManyField(District, blank=True)

    def __str__(self):
        return f'{self.id}: {self.street_address}'

 
class SendingSite(Site):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sending_sites")
    transfer_purpose = models.IntegerField(choices = TRANSFER_PURPOSES) # Tree, housing, historic landmark
    transferrable_far = models.FloatField(null=True, blank=True)

class ReceivingSite(Site):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiving_sites")
    target_far = models.FloatField() # desired FAR to receive
    





DOCUMENT_PURPOSES = (
    (0, "City Forester or arborist certification"),
    (1, "PHB certification"),
    (2, "Other certification"),
    (3, "Other supporting document"),
)

class SupportingDocument(models.Model):
    class Meta:
        abstract = True # django passes over this model when making migrations unless it's inherited

    document_purpose = models.IntegerField(choices = DOCUMENT_PURPOSES)

    def __str__(self):
        return f'[{self.id}] {self.document_purpose[1]} for {self.site}'

# https://stackoverflow.com/questions/22538563/django-reverse-accessors-for-foreign-keys-clashing
class SendingSiteDoc(SupportingDocument):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="%(class)s_supporting_docs")
    site = models.ForeignKey(SendingSite, on_delete=models.CASCADE, related_name="supporting_docs")

class ReceivingSiteDoc(SupportingDocument):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="%(class)s_supporting_docs")
    site = models.ForeignKey(ReceivingSite, on_delete=models.CASCADE, related_name="supporting_docs")







# to see all fiels, do `dir(object.object)` for example 
# x = SendingSite.objects.first() # <- first row
# dir(x.location)

class InvalidBid(Exception):
    pass

class Auction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions")
    sending_site = models.OneToOneField(SendingSite, on_delete=models.DO_NOTHING)
    created = models.DateTimeField(auto_now_add=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    starting_price_sqft = models.FloatField(default=1.0)
    reserve_price_sqft = models.FloatField(default=0.0) # reserve price per square foot

    # not completed until transaction finalized
    # receiving_site = models.OneToOneField(ReceivingSite, on_delete=models.DO_NOTHING)

    def validate_bid(self, user, amount):
        if amount < self.starting_price_sqft:
            raise InvalidBid('Bid amount too low. Must bid higher.')

        if not self.start < timezone.now() < self.end:
            raise InvalidBid('Auction is closed.')

        if self.user == user:
            raise InvalidBid('Cannot bid on your own auction.')

        bids = self.bids.all()
        if bids:
            max_bid = bids.aggregate(models.Max('amount'))
            if amount <= max_bid.amount:
                raise InvalidBid('Bid amount too low. Must bid higher.')
    
    def current_bid(self):
        bids = self.bids.all()
        max_bid = bids.aggregate(models.Max('amount'))
        if not max_bid['amount__max']:
            #No bids yet
            return self.starting_price_sqft
        else:
            return max_bid

    def add_bid(self, user, amount):
        amount = abs(amount)
        self.validate_bid(user, amount)

        bid = Bid(user = user, auction = self, amount = amount)
        bid.save()
        return bid
        
    def __str__(self):
        return f'[{self.id}] Auction for {self.sending_site.street_address} from {self.user}'


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bids")
    amount = models.FloatField()
    created = models.DateTimeField(auto_now_add=True)
    receiving_site = models.ForeignKey(ReceivingSite, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="bids")
