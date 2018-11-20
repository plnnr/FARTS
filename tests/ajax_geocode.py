import requests 
import os

def address_search_ajax(client_input="109 NE Han"):
    # TODO: move this token to Django settings from an environment variable
    pmap_server_api_key = os.getenv("PORTLAND_MAPS_SERVERSIDE_API_KEY")
    base_url = "https://www.portlandmaps.com/locator/Default/GeocodeServer/findAddressCandidates/?Single%20Line%20Input="
    url_appendix = f"&f=json&outSR=%7B%22wkid%22%3A102100%7D&maxLocations=10&landmarks=1&id_matches=1&alt_ids=1&centerline=1&api_key={pmap_server_api_key}"
    fetch_url = base_url+client_input+url_appendix
    response = requests.get(fetch_url)
    print(response.json())

address_search_ajax()
