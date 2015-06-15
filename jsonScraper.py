from lxml import html
import requests
from enumerators import SiteTypes
from enumerators import PaginationTypes
from event import Event
import sys

class JsonScraper:
  def __init__(self, sent_url, name, param):
    self.url = sent_url
    self.param = param
    self.name = name
    self.eventResults = ""
    self.eventName = ""
    self.description = []
    self.eventTime = []
    self.image = ""
    self.location = []
    self.price = ""
    self.allEvents = []

  def parse(self):
    i=1
    sendUrl = self.url + self.param + str(i)
    print sendUrl

    results = requests.get(sendUrl)
    keepGoing = True

    while keepGoing:
      print "Parsing: " + str(i)
      obj = results.json()
      keepGoing = self.parseOneJson(obj)
      i+=1
      sendUrl = self.url + self.param + str(i)
      results = requests.get(sendUrl)

  def parseOneJson(self, obj):
    count = 0;
    if ((obj[self.eventResults] is not None) and (len(obj[self.eventResults])>0)):
      for result in obj[self.eventResults]:
        count += 1
        sys.stdout.write("\rGetting " + str(count) + " of " + str(len(obj[self.eventResults])))
        sys.stdout.flush()
        event = Event()
        event.name = self.checkIfList(self.eventName, result)
        event.location = self.checkIfList(self.location, result)
        event.description = self.checkIfList(self.description, result)
        event.datetime = self.checkIfList(self.eventTime, result)
        event.price = self.checkIfList(self.price, result)
        event.imagePath = self.checkIfList(self.image, result)
        event.dump = self.checkIfList(self.description, result)
        event.forceStr()
        self.allEvents.append(event)
      print "\n"
      return True
    else:
      return False


  def checkIfList(self, item, result):
    storeObj = ""
    #print type(item)
    #print "----item---"
    #print item
    if type(item) is list:
      if len(item)>0:
        for oneItem in item:
          oneItem = str(oneItem)
          #print "------oneItem------"
          #print oneItem
          goDeep = oneItem.split(" ")
          #print "------goDeep------"
          #print goDeep
          wait = result
          for go in goDeep:
            wait = wait[go]
          #print "------wait------"
          #print wait
          if (((type(wait) is str) or (type(wait) is unicode)) and (wait != "")):
            wait = str(wait)
            storeObj = storeObj + wait + ", "
    elif type(item) is str or type(item) is unicode:
      item = str(item)
      if item != "":
        storeObj = result[item]
    elif type(item) == None:
      storeObj = ""
    return storeObj