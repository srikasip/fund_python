import requests
import json
import sys
#from apiclient.discovery import build
import requests
from pprint import pprint

class GoogleHelper:
  def __init__(self, sent_apikey=None):
    if sent_apikey != None:
      self.apikey = sent_apikey

  def getPlaceInfo(self, searchString):
    #service = build('maps', 'v1', developerKey=self.apikey)
    #params = [self.apikey, searchString]
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json?key={0}&query={1}".format(self.apikey, searchString)

    address = {"search_string": searchString}

    try:
      result = requests.get(url)
      places = result.json()

      if places["status"] == "OK":
        if len(places["results"])>0:
          place = places["results"][0]
          address["address"] = place["formatted_address"]
          address["place_id"] = place["place_id"]
          address["lat"] = place["geometry"]["location"]["lat"]
          address["long"] = place["geometry"]["location"]["lng"]
          address["name"] = place["name"]
          address["types"] = place["types"]
          address["status"] = "checked"
        else:
          address["status"] = "no result"
          address["address"] = searchString
      else:
        address["status"] = "error"
        address["address"] = searchString
        address["errorMessage"] = "Google Replied with an Error"
    except:
      address["status"] = "error"
      address["address"] = searchString
      if len(sys.exc_info()[0])>0:
        address["errorMessage"] = str(sys.exc_info()[0])
      else:
        address["errorMessage"] = "Failed for unknown reason!"
        
    return address