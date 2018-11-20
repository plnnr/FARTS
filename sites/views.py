from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.gis.measure import D
from django.contrib.gis.geos import GEOSGeometry

import requests
import os

from sites.models import SendingSite

##### Utilities #####
def build_query_params(params):
    param_string = "?"
    for key, value in params.items():
        param_string += f"{key}={value}&"
    return param_string

#####################

def test_geospatial(request):
    x = -122.66392  # -13654885.113
    y = 45.536522  # 5675877.183
    point = GEOSGeometry(f'POINT({x} {y})', srid=4326)

    result = SendingSite.objects.filter(
        location__distance_lte=(point, D(mi=2))
    )
    import pdb
    pdb.set_trace()


def default_map(request):
    # specify path to template here
    # TODO: move this token to Django settings from an environment variable
    # found in the Mapbox account settings and getting started instructions
    # see https://www.mapbox.com/account/ under the "Access tokens" section
    mapbox_access_token = 'pk.eyJ1IjoibmtvYmVsIiwiYSI6ImNqbzF4M3Q4ODBnZHoza254dWplOGk5ZnAifQ.TKDCR6nbv268FBi68MSbiA'
    context = {'mapbox_access_token': mapbox_access_token}
    return render(request, 'sites/default.html', context)


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


# if sendingsite.historic_district == True:
    #


def get_tract_fips_lat_lng(raw_address, raw_city, raw_state):
    address = raw_address
    city = raw_city
    state = raw_state
    geocoding_base_url = "https://geocoding.geo.census.gov/geocoder/geographies/address?"
    address_url = f"street={address.replace(' ', '+').replace('.', '')}&city={city}&state={state}"
    benchmark_etc_url = "&benchmark=Public_AR_Census2010&vintage=Census2010_Census2010&format=json"

    url_to_geocode = geocoding_base_url+address_url+benchmark_etc_url
    
    print(f"Geocoding request at following URL:\n{url_to_geocode}")
    
    with urllib.request.urlopen(url_to_geocode) as response:
        geocoding_response = json.load(response)
        # pprint(geocoding_response)
    
    try:
        # tract_geoid = geocoding_response['result']['addressMatches'][0]['geographies']['Census Tracts'][0]['GEOID']
        tract6 = geocoding_response['result']['addressMatches'][0]['geographies']['Census Tracts'][0]['TRACT']
        state_fips = geocoding_response['result']['addressMatches'][0]['geographies']['Census Tracts'][0]['STATE']
        county_fips = geocoding_response['result']['addressMatches'][0]['geographies']['Census Tracts'][0]['COUNTY']
        county_name = geocoding_response['result']['addressMatches'][0]['geographies']['Counties'][0]['NAME']
        lat = geocoding_response['result']['addressMatches'][0]['coordinates']['x']
        lng = geocoding_response['result']['addressMatches'][0]['coordinates']['y']
    except IndexError as e:
        print(f"IndexError occurred:\t{e}")
        if geocoding_response['result']['addressMatches'] == []:
            print(f"No matching geocoding results for '{address}, {city}, {state}.'")

    return tract6, county_fips, state_fips, lat, lng, county_name

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
    
    response = requests.get(alt_fetch_url)
    return JsonResponse(response.json())



def get_landuse_details_ajax(request):
    site_coords_raw = request.GET.get('site_coords', '') 
    site_coords = site_coords_raw.split(',')
    x = site_coords[0]
    y = site_coords[1]
    xyobj = '{"x":' + x + ',"y":' + y + '}'
    # TODO: move this token to Django settings from an environment variable
    pmap_server_api_key = os.getenv("PORTLAND_MAPS_SERVERSIDE_API_KEY")

    # query parameters for getting zoning and land use information
    landuse_params = {
        'detail_type': 'zoning',
        'sections': '*',
        'geometry': f'{xyobj}', # { "x" : -13653136.529, "y" : 5705641.378}
        'api_key': f'{pmap_server_api_key}',
    }

    query_params = build_query_params(landuse_params)
    base_url = "https://www.portlandmaps.com/api/detail/"
    fetch_url = base_url + query_params

    response = requests.get(fetch_url)

    return JsonResponse(response.json())

#work: 
#https://www.portlandmaps.com/api/detail/?&detail_type=zoning&sections=*&geometry={%20"x"%20:%20-13653136.529,%20"y"%20:%205705641.378}

#doesn't:
#https://www.portlandmaps.com/api/detail/?detail_type=zoning&sections=*&detail_id=&geometry={%22x%22:-13654362.408,%22y%22:5708284.816}&property_id=&file_type=&file_id=&cache_clear=&format=&callback=

# landuse_params = {
#         'detail_type': 'zoning',
#         'sections': '*',
#         'detail_id': '',
#         'geometry': f'{xyobj}', # { "x" : -13653136.529, "y" : 5705641.378}
#         'property_id': '',
#         'file_type': '',
#         'file_id': '',
#         'cache_clear': '',
#         'format': '',
#         'callback': '',
#         'api_key': f'{pmap_server_api_key}',
# }