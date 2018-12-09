from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.gis.measure import D
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.auth.decorators import login_required

import requests
import os
import json
from random import *

from sites.forms import AuctionForm
from sites.models import SendingSite, ReceivingSite, District, BaseZoneClass, BaseZone, Auction, Bid

##### Utilities #####
def build_query_params(params):
    param_string = "?"
    for key, value in params.items():
        param_string += f"{key}={value}&"
    return param_string


def get_landuse_details_ajax(request):
    site_coords_raw = request.GET.get('site_coords', '') 
    site_coords = site_coords_raw.split(',')
    x = site_coords[0]
    y = site_coords[1]
    xyobj = '{"x":' + x + ',"y":' + y + '}'
    pmap_server_api_key = os.getenv("PORTLAND_MAPS_SERVERSIDE_API_KEY")

    # query parameters for getting zoning and land use information
    landuse_params = {
        'detail_type': 'zoning',
        'sections': '*',
        'geometry': f'{xyobj}', # {"x":-13654362.408,"y":5708284.816}
        'format': 'json',
        'api_key': f'{pmap_server_api_key}',
    }

    query_params = build_query_params(landuse_params)
    base_url = "https://www.portlandmaps.com/api/detail/"
    fetch_url = base_url + query_params

    response = requests.get(fetch_url)

    landuse = response.json()
    assessor = get_assessor_details_ajax(request)
    property = get_property_details_ajax(request)

    return JsonResponse({
        'landuse': landuse,
        'assessor': assessor,
        'property': property,
    })


# http://localhost:8000/search?address_part=1220%20NE%2017
def address_search_ajax(request):
    client_input = request.GET.get('address_part', '')
    # TODO: move this token to Django settings from an environment variable
    pmap_server_api_key = os.getenv("PORTLAND_MAPS_SERVERSIDE_API_KEY")
    # Address candidate service docs: https://www.portlandmaps.com/arcgis/sdk/rest/index.html#/Find_Address_Candidates/02ss00000015000000/
    base_url = "https://www.portlandmaps.com/locator/Default/GeocodeServer/findAddressCandidates/?Single%20Line%20Input="
    url_params = f"&f=json&alt_coords=1&maxLocations=5&landmarks=1&id_matches=1&alt_ids=1&centerline=1&api_key={pmap_server_api_key}"
    fetch_url = base_url+client_input+url_params

    alt_base_url = "https://www.portlandmaps.com/api/suggest/?"
    alt_url_params = f"&alt_coords=1&api_key={pmap_server_api_key}&query={client_input}"
    alt_fetch_url = alt_base_url + alt_url_params
    
    # import pdb; pdb.set_trace()
    response = requests.get(alt_fetch_url)
    
    return JsonResponse(response.json())


def get_assessor_details_ajax(request):
    site_coords_raw = request.GET.get('site_coords', '') 
    site_coords = site_coords_raw.split(',')
    x = site_coords[0]
    y = site_coords[1]
    xyobj = '{"x":' + x + ',"y":' + y + '}'
    pmap_server_api_key = os.getenv("PORTLAND_MAPS_SERVERSIDE_API_KEY")

    assessor_params = {
        'detail_type': 'assessor',
        'sections': '*',
        'geometry': f'{xyobj}', # { "x" : -13653136.529, "y" : 5705641.378}
        'format': 'json',
        'api_key': f'{pmap_server_api_key}',
    }
    
    query_params = build_query_params(assessor_params)
    base_url = "https://www.portlandmaps.com/api/detail/"
    fetch_url = base_url + query_params

    response = requests.get(fetch_url)

    return response.json()

def get_property_details_ajax(request):
    site_coords_raw = request.GET.get('site_coords', '') 
    site_coords = site_coords_raw.split(',')
    x = site_coords[0]
    y = site_coords[1]
    xyobj = '{"x":' + x + ',"y":' + y + '}'
    pmap_server_api_key = os.getenv("PORTLAND_MAPS_SERVERSIDE_API_KEY")

    assessor_params = {
        'detail_type': 'property',
        'sections': '*',
        'geometry': f'{xyobj}', # { "x" : -13653136.529, "y" : 5705641.378}
        'format': 'json',
        'api_key': f'{pmap_server_api_key}',
    }
    
    query_params = build_query_params(assessor_params)
    base_url = "https://www.portlandmaps.com/api/detail/"
    fetch_url = base_url + query_params

    response = requests.get(fetch_url)

    return response.json()

def make_fuzzy_POINT(x, y):
    ### Adds noise to an exact location and returns a PostGIS point
    numbers = list(range(-1000,-500)) + list(range(500,1000))
    scale_adjustment = 180000. # larger number = more randomization

    x_offset = choice(numbers)
    y_offset = choice(numbers)
    
    x_fuzzy = x + x_offset / scale_adjustment
    y_fuzzy = y + y_offset / scale_adjustment

    fuzzy_point = GEOSGeometry(f'POINT({y_fuzzy} {x_fuzzy})', srid=4326)

    return fuzzy_point

#####################

def test_geospatial(request):
    x = -122.66392  # -13654885.113
    y = 45.536522  # 5675877.183
    point = GEOSGeometry(f'POINT({x} {y})', srid=4326)

    result = SendingSite.objects.filter(
        location__distance_lte=(point, D(mi=2))
    )
    import pdb; pdb.set_trace()

@login_required
def sending_site(request):
    # specify path to template here
    # TODO: move this token to Django settings from an environment variable
    # found in the Mapbox account settings and getting started instructions
    # see https://www.mapbox.com/account/ under the "Access tokens" section
    mapbox_access_token = 'pk.eyJ1IjoibmtvYmVsIiwiYSI6ImNqbzF4M3Q4ODBnZHoza254dWplOGk5ZnAifQ.TKDCR6nbv268FBi68MSbiA'
    context = {'mapbox_access_token': mapbox_access_token}
    return render(request, 'sites/register-sending.html', context)

@login_required
def receiving_site(request):
        # specify path to template here
    # TODO: move this token to Django settings from an environment variable
    # found in the Mapbox account settings and getting started instructions
    # see https://www.mapbox.com/account/ under the "Access tokens" section
    mapbox_access_token = 'pk.eyJ1IjoibmtvYmVsIiwiYSI6ImNqbzF4M3Q4ODBnZHoza254dWplOGk5ZnAifQ.TKDCR6nbv268FBi68MSbiA'
    context = {'mapbox_access_token': mapbox_access_token}
    return render(request, 'sites/register-receiving.html', context)

def home(request):
    context = {}
    return render(request, 'home.html', context)

def about(request):
    context = {}
    return render(request, 'about.html', context)

def rules(request):
    context = {}
    return render(request, 'rules.html', context)


# to see all fiels, do `dir(object.object)` for example
# x = SendingSite.objects.first() # <- first row
# dir(x.location)

def determine_eligibility_receiving(receiving_site):
    eligible = False
    if receiving_site.historic_district != True:
        eligible = True
    if receiving_site.conservation_district != True:
        eligible = True
    if receiving_site.plan_district not in ["Central City Plan District", "Central City/South Auditorium"]:
        eligible = True
    return eligible

def determine_eligibility_match(sending_site, receiving_site):
    eligible = False
    warning = ''
    if sending_site.base_zone_class == receiving_site.base_zone_class:
        eligible = True
    if sending_site.credit_sqft > receiving_site.credit_max_sqft:
        warning += "Sending site credit total exceeds receiving site allowable maximum"
    return eligible, warning


@login_required
def record_receiving_site(request):
    data = json.loads(request.body)
    
    x = data['x_coord'] # -122.66392  # -13654885.113
    y = data['y_coord'] # 45.536522  # 5675877.183
    point = GEOSGeometry(f'POINT({y} {x})', srid=4326)

    fuzzy_point = make_fuzzy_POINT(x, y)

    # import pdb; pdb.set_trace()
    # coordinates= models.PointField(srid=4326,default='SRID=3857;POINT(0.0 0.0)')

    site = ReceivingSite()

    site.street_address = data['street_address']
    site.site_size = data['site_size']
    site.building_size = data['building_size']
    site.site_far = data['site_far']
    site.location = point
    site.fuzzy_location = fuzzy_point

    site.pmaps_object = data['raw_data']
    site.parcel_poly = json.dumps(data['raw_data']['taxlotGeometry']['geometry'])

    site.target_far = data['target_far']
    site.user = request.user

    site.save() # must save first before adding many to many relationship

    for zone in data['base_zones']:
        base_zone, _ = BaseZone.objects.get_or_create(name = zone)
        site.base_zones.add(base_zone)
    
    for zone in data['base_zone_classes']:
        zone_class, _ = BaseZoneClass.objects.get_or_create(name=zone)
        site.base_zone_classes.add(zone_class)

    for district_name in data['districts']:
        district, _ = BaseZoneClass.objects.get_or_create(name=district_name)
        site.base_zone_classes.add(district)

    return JsonResponse({'id': site.id})
    

@login_required
def record_sending_site(request):
    data = json.loads(request.body)
    
    x = data['x_coord'] # -122.66392  # -13654885.113
    y = data['y_coord'] # 45.536522  # 5675877.183
    point = GEOSGeometry(f'POINT({y} {x})', srid=4326)

    fuzzy_point = make_fuzzy_POINT(x, y)


    # import pdb; pdb.set_trace()

    # import pdb; pdb.set_trace()
    # coordinates= models.PointField(srid=4326,default='SRID=3857;POINT(0.0 0.0)')

    site = SendingSite()

    site.street_address = data['street_address']
    site.site_size = data['site_size']
    site.building_size = data['building_size']
    site.site_far = data['site_far']
    site.location = point
    site.fuzzy_location = fuzzy_point

    site.pmaps_object = data['raw_data']
    site.parcel_poly = json.dumps(data['raw_data']['taxlotGeometry']['geometry'])

    site.transferrable_far = data['transferrable_far']
    site.transfer_purpose = data['transfer_purpose']
    site.user = request.user

    site.save() # must save first before adding many to many relationship

    for zone in data['base_zones']:
        base_zone, _ = BaseZone.objects.get_or_create(name = zone)
        site.base_zones.add(base_zone)
    
    for zone in data['base_zone_classes']:
        zone_class, _ = BaseZoneClass.objects.get_or_create(name=zone)
        site.base_zone_classes.add(zone_class)

    for district_name in data['districts']:
        district, _ = BaseZoneClass.objects.get_or_create(name=district_name)
        site.base_zone_classes.add(district)

    return JsonResponse({'id': site.id})

def get_bids(id):
    bid = Bid.objects.filter(receiving_site__id=id)
    return bid  

def make_bid(request, id):
    ...

def view_auction(request, id):
    auction = get_object_or_404(Auction, sending_site__id=id)
    sending_site = auction.sending_site
    
    context = {
        'sendingSite': sending_site,
        'auction': auction,
    }
    auction.current_bid()
    ##import pdb; pdb.set_trace()
    return render(request, 'sites/view_auction.html', context)

    

@login_required
def view_receiving(request):
    receiving_sites = ReceivingSite.objects.filter(user=request.user)

    ### import pdb; pdb.set_trace()
    context = {
        'receiving_sites': receiving_sites,
    }
    return render(request, 'sites/list-receiving.html', context)

@login_required
def view_receiving_sites(request):
    receiving_sites = ReceivingSite.objects.filter(user=request.user)
    data = []

    for site in receiving_sites:
        bid_status = Bid.objects.filter(receiving_site__id=site.id).exists()
        data.append({
            'id': site.id,
            'streetAddress': site.street_address,
            'bidStatus': bid_status,
            'user': site.user.username,
        })

    return JsonResponse({'sites': data})


def get_auction(id):
    auction = Auction.objects.filter(sending_site__id=id)
    return auction

## Would have been a good opportunity for Vue below
@login_required
def view_sending(request):
    sending_sites = SendingSite.objects.filter(user=request.user)
    
    auctions = {}
    for site in sending_sites:
        if len(get_auction(site.id)) == 0:
            auctions[f'{site.id}'] = None
        else:
            auctions[f'{site.id}'] = get_auction(site.id)
    auctions = {site.id: get_auction(site.id) for site in sending_sites}
    ### import pdb; pdb.set_trace()
    context = {
        'sending_sites': sending_sites,
        'auctions': auctions,
    }
    return render(request, 'sites/list-sending.html', context)

@login_required
def view_sending_sites(request):
    sending_sites = SendingSite.objects.filter(user=request.user)
    data = []

    for site in sending_sites:
        auction_status = Auction.objects.filter(sending_site__id=site.id).exists()
        data.append({
            'id': site.id,
            'streetAddress': site.street_address,
            'auctionStatus': auction_status,
            'user': site.user.username,
        })

    return JsonResponse({'sites': data})

def get_auction_activity(id):
    auction = Auction.objects.filter(sending_site__id=id)

@login_required
def receiving_site_details(request, id):
    receiving_site = get_object_or_404(ReceivingSite, id=id)
    return render(request, 'sites/receiving_site_detail.html', {'object': receiving_site})


@login_required
def sending_site_details(request, id):
    sending_site = get_object_or_404(SendingSite, id=id)
    return render(request, 'sites/sending_site_detail.html', {'object': sending_site})

@login_required
def create_auction(request):
    if request.method == 'POST':
        form = AuctionForm(request.user, request.POST)

        if form.is_valid():
            auction = form.save(commit=False)
            auction.user = request.user
            auction.save()

            return redirect('/accounts/dashboard')
    else:
        form = AuctionForm(request.user)

    return render(request, 'sites/create_auction.html', {'form': form})
    # request.GET.get('user')

    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions")
    # sending_site = models.OneToOneField(SendingSite, on_delete=models.DO_NOTHING)
    # created = models.DateTimeField(auto_now_add=True)
    # start = models.DateTimeField()
    # end = models.DateTimeField()
    # starting_price_sqft = models.FloatField(default=1.0)
    # reserve_price_sqft = models.FloatField(default=0.0)
