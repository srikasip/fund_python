import requests
import json
from pprint import pprint
import re
import sys
import pyap
import os

def main():
  with open('EventsOutput/allOutput.json') as output_file:
    events = json.load(output_file) 


  events = DateHelper(events)
  events = TimeHelper(events)
  events = pyapHelper(events)
  #events = LocationHelper(events)


  silentRemove("EventsOutput/allProcessedData.json")

  with open("EventsOutput/allProcessedData.json", "w") as f:
    f.write(json.dumps(events))


def DateHelper(events):
  hold = []
  all_dates = []
  for event in events["event"]:
    hold = cleanDate(event["dump"])
    #hold = cleanDate(event["datetime"])
    if len(hold) == 0:
      hold = cleanDate(event["description"])
    if len(hold) == 0:
      pass#hold = cleanDate(event["location"])

    event["date"] = hold
    all_dates.append(hold)

  counter = 0
  emptyCounter = 0
  for date in all_dates:
    if len(date)>0:
      counter += 1
    else:
      emptyCounter += 1

  print "-------------------------------------\n\r"
  print "Total Num Events: " + str(len(all_dates))
  print "Non-empty Dates: " + str(counter)
  print "Empty Dates: " + str(emptyCounter)

  return events

def TimeHelper(events):
  all_times = []
  hold = []
  for event in events["event"]:
    hold = cleanTimes(event["datetime"])
    hold += cleanTimes(event["dump"])
    #hold += cleanTimes(event["description"])
    #hold += cleanTimes(event["location"])
    event["time"] = hold
    all_times.append(hold)

  counter = 0
  emptyCounter = 0
  for time in all_times:
    if len(time)>0:
      counter += 1
    else:
      emptyCounter += 1

  print "-------------------------------------\n\r"
  print "Total Num Events: " + str(len(all_times))
  print "Non-empty Times: " + str(counter)
  print "Empty Times: " + str(emptyCounter)
  

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

def LocationHelper(events):
  api_key = "AIzaSyDu7T68ilHqAuxc9wDjjnyoCbf5F-lSWXs"
  goog = GoogleHelper(api_key)
  all_locations = []

  counter = 1
  for event in events["event"]:
    try:
      address = goog.getPlaceInfo(event["location"].encode("utf-8"))
      event["address"] = address
      all_locations.append(address)
      sys.stdout.write("\rDoing thing " + str(counter))
      sys.stdout.flush()
    finally:
      counter+=1

  counter = 0
  emptyCounter = 0

  for ady in all_locations:
    if ady["status"] == "checked":
      counter += 1
    else:
      emptyCounter += 1

  print "-------------------------------------\n\r"
  print "Total Num Events: " + str(len(all_locations))
  print "Non-empty Locations: " + str(counter)
  print "Empty Locations: " + str(emptyCounter)


  return events

def cleanTimes(timeStringy):
  randomHold = timeStringy
  times = []
  #(\d+(am|pm|:)?(-|\sto\s))?\d+[:]?\d*(am|pm|:)\d*
  p = re.compile(r'(\d+\s*(am|pm|:)?\s*(-|to)\s*)?\d+[:]?\d*\s*(am|pm|:)\d*', re.IGNORECASE)
  m = p.search(randomHold)
  if m:
    #print type(m.group())
    times.append(m.group())
  return times


def cleanDate(dateStringy):
  randomHold = dateStringy
  #step 1: Basic set of possible month values
  month_words = ["january","february","march","april","may","june","july","august","september","october","november","december","jan","feb","mar","apr","may","jun","jul","aug","sept","oct","nov","dec"]
  month_nums = ["1","2","3","4","5","6","7","8","9","10","11","12","01","02","03","04","05","06","07","08","09"]
  days = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31","01","02","03","04","05","06","07","08","09"]
  years = ["2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020","2021","2022"]
  stopWords = [" the ", " of ", "  ", "  "]
  numEndings = ["th", "st", "nd", "rd"]
  specialChars = ["\"", "'", ",", ".", "|", "-"]

  #step 2: check to see if you can find the month string anywhere
  dateString =  my_replace(randomHold, stopWords, " ")
  wordArr = dateString.split(" ")
  holdword = ""
  counter = 0
  dates = []

  for i in range(0,len(wordArr)):
    month, day, year = "", "", ""
    holdword = my_replace(wordArr[i].lower(), specialChars)
    if holdword in month_words:
      month = wordArr[i]
      lower = i - min(i,4)
      upper = i + min(len(wordArr)-i-1, 4)
      for j in range(lower, upper):
        if my_replace(wordArr[j],specialChars+numEndings) in days:
          day = my_replace(wordArr[j],specialChars+numEndings)
        elif my_replace(wordArr[j],specialChars) in years:
          year = my_replace(wordArr[j],specialChars)

      actualDateString = month + " " + day + ", " + year
      dates.append(actualDateString)

  if len(dates)==0:
    dateString = dateStringy.replace(" ", "")
    p = re.compile(r'\d{1,4}[/-]\d{1,2}[/-]\d{1,4}')
    m = p.match(dateString)
    if m:
      dates.append(m.group())
    else:
      p = re.compile(r'\d{1,2}[/-]\d{1,2}')
      m = p.match(dateString)
      if m:
        dates.append(m.group())

  return dates


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