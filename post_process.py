import requests
import json
from pprint import pprint
import re
import sys
import pyap
import os
from dateparsing import DateParser
from timeparsing import TimeParser
from priceparsing import PriceParser
from proximity import ProximityParser

def main():
  with open('EventsOutput/allOutput.json') as output_file:
    events = json.load(output_file) 


  events = DateHelper(events)
  events = TimeHelper(events)
  events = PriceHelper(events)
  events = pyapHelper(events)
  events = ProximityDetection(events)
  #events = LocationHelper(events)
  events = RemoveDump(events)


  silentRemove("EventsOutput/allProcessedData.json")

  with open("EventsOutput/allProcessedData.json", "w") as f:
    f.write(json.dumps(events))


def RemoveDump(events):
  for event in events["event"]:
    event["dump"] = ""

  return events

def DateHelper(events):

  dateHelper = DateParser(events["event"], ["datetime", "dump"])
  events["event"] = dateHelper.doParse()

  return events

def TimeHelper(events):
  timeHelper = TimeParser(events["event"], ["datetime", "dump"])
  events["event"] = timeHelper.doParse()
  
  return events

def PriceHelper(events):
  priceHelper = PriceParser(events["event"], ["price", "dump"])
  events["event"] = priceHelper.doParse()

  return events

def ProximityDetection(events):
  proxHelp = ProximityParser(events["event"], ["datetime", "dump"])
  events["event"] = proxHelp.LinkTimes()
  proxHelp.events = events["event"]
  events["event"] = proxHelp.LinkDates()
  events["event"] = proxHelp.LinkDateToTime()

  return events

def pyapGetEvent_Locations(searchString):
  addresses = pyap.parse(searchString.encode("utf-8"), country='US')
  event_locations = {"numLocations":len(addresses), "addresses":[]}
  #"searchString":searchString,
  for address in addresses:
    addDict = address.as_dict()
    event_locations["addresses"].append(addDict)

  return event_locations


def pyapHelper(events):
  all_locations = []
  for event in events["event"]:
    eloc = pyapGetEvent_Locations(event["location"])
    if eloc["numLocations"]==0:
      eloc = pyapGetEvent_Locations(event["dump"])
    #  eloc = pyapGetEvent_Locations(event["description"])
    event["addresses"] = eloc
    all_locations.append(eloc)
  
  counter = 0
  emptyCounter = 0

  for ady in all_locations:
    if ady["numLocations"]>0:
      counter += 1
    else:
      emptyCounter += 1
  
  print "-------------------------------------\n\r"
  print "Total Num Events: " + str(len(all_locations))
  print "Non-empty Locations: " + str(counter)
  print "Empty Locations: " + str(emptyCounter)

  return events

# def LocationHelper(events):
#   api_key = "AIzaSyDu7T68ilHqAuxc9wDjjnyoCbf5F-lSWXs"
#   goog = GoogleHelper(api_key)
#   all_locations = []

#   counter = 1
#   for event in events["event"]:
#     try:
#       address = goog.getPlaceInfo(event["location"].encode("utf-8"))
#       event["address"] = address
#       all_locations.append(address)
#       sys.stdout.write("\rDoing thing " + str(counter))
#       sys.stdout.flush()
#     finally:
#       counter+=1

#   counter = 0
#   emptyCounter = 0

#   for ady in all_locations:
#     if ady["status"] == "checked":
#       counter += 1
#     else:
#       emptyCounter += 1

#   print "-------------------------------------\n\r"
#   print "Total Num Events: " + str(len(all_locations))
#   print "Non-empty Locations: " + str(counter)
#   print "Empty Locations: " + str(emptyCounter)


#   return events

def cleanTimes(timeStringy):
  randomHold = timeStringy
  times = []
  #(\d+(am|pm|:)?(-|\sto\s))?\d+[:]?\d*(am|pm|:)\d*
  #p = re.compile(r'(\d+\s*(am|pm|:)*\s*\d*)(\s*(-|to)\s*)*(\d+[:]?\d*\s*(am|pm|:)\d*)*', re.IGNORECASE)
  p = re.compile(r'(\d+\s*(am|pm|:)?\s*(-|to)\s*)?\d+[:]?\d*\s*(am|pm|:)\d*', re.IGNORECASE)
  m = p.search(randomHold)
  if m:
    #print type(m.group())
    times.append(m.group())
  return times


def my_replace(sentString, delims, replacer = ""):
  holdString = sentString
  for delim in delims:
    holdString = holdString.replace(delim, replacer)

  return holdString

def silentRemove(filename):
  try:
    os.remove(filename)
  except OSError:
    pass

if __name__ == "__main__": main()