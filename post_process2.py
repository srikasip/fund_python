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
  #Here is the list of things that have to be done
  #1. Get the unprcessed json data!
  #2. Iterate through each and every single event (which would be one single JSON object)
  #3a. For each iteration, lets start with get the date!  maybe we should do that as a seperate python script!
       #return the date string potential, the location, and some kind of a score.
  #3b. For each iteration, lets then do the time stuff! maybe we should do that as a seperate python script too!
        #return the time string potential, the location, and some kind of a score.
  #3c. For each iteration, get the address string from the text


  #1. Get the uprocessed json data and hold it in an object.
  with open('EventsOutput/trial_Output.json') as output_file:
    events = json.load(output_file)

  events["event"] = DateHelper(events["event"])
  events["event"] = TimeHelper(events["event"])
  events["event"] = PriceHelper(events["event"])
  events["event"] = LocationHelper(events["event"])
  events["event"] = ProximityDetection(events["event"])



def DateHelper(sentArray):
  
  dateHelper = DateParser(sentArray, ["datetime", "dump"])
  sentArray = dateHelper.doParse()

  return sentArray
  # for event in sentArray:
  #   print event["date"]


def TimeHelper(sentEvents):
  timeHelper = TimeParser(sentEvents, ["datetime", "dump"])
  sentEvents = timeHelper.doParse()

  # for event in sentEvents:
  #   if len(event["time"])<1:
  #     pass#print event["datetime"]

  return sentEvents
def PriceHelper(sentEvents):
  priceHelper = PriceParser(sentEvents, ["price", "dump"])
  sentEvents = priceHelper.doParse()

  # for event in sentEvents:
  #   if len(event["pPrice"])<1:
  #     print event["price"]
  #     print event["pPrice"]

  return sentEvents

def LocationHelper(events):
  all_locations = []
  for event in events:
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

def pyapGetEvent_Locations(searchString):
  addresses = pyap.parse(searchString.encode("utf-8"), country='US')
  event_locations = {"numLocations":len(addresses), "addresses":[]}
  #"searchString":searchString,
  for address in addresses:
    addDict = address.as_dict()
    event_locations["addresses"].append(addDict)



  return event_locations


def ProximityDetection(sentEvents):
  proxHelp = ProximityParser(sentEvents, ["datetime", "dump"])
  sentEvents = proxHelp.LinkTimes()
  proxHelp.events = sentEvents 
  sentEvents = proxHelp.LinkDates()
  sentEvents = proxHelp.LinkDateToTime()

  return sentEvents
  #proxHelp.canonicalizeTime2("2-to-5pm")

if __name__ == "__main__": main()