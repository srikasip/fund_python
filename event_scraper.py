#!/usr/bin/python3
#this is a generic events scraper that uses user-submitted data on a site to scrape events

from lxml import html
import requests
from enumerators import SiteTypes
from enumerators import PaginationTypes
from event import Event
from sitetext import SiteText

#This class has the following variables
#######  self.url --> This is the url to the main document

#######  self.siteType --> this is an enumerated description of what a site is.  are all the event details in a list? Is this a list that points to individual event pages, which house event details??
#######  self.eventDetailsPageLink_xpath

####### self.url
####### self.siteType
####### self.pagination_xpath
####### self.paginationType
####### self.eventDetailsPageLink_xpath
####### self.eventName_xpath
####### self.eventLocation_xpath
####### self.eventDateTime_xpath
####### self.eventDescription_xpath 
####### self.eventPrice_xpath
####### self.allEvents
  

class EventScraper:
  def __init__ (self, sent_url, sent_type=SiteTypes.ListLinks, sent_pagination="none", paginationType = PaginationTypes.NextPage):
    self.url = sent_url
    self.domain = ""
    self.siteType = sent_type
    self.pagination_xpath = sent_pagination
    self.paginationType = paginationType
    self.eventDetailsPageLink_xpath = ''
    self.eventName_xpath = ''
    self.eventLocation_xpath = ''
    self.eventDateTime_xpath = ''
    self.eventDescription_xpath = ''
    self.eventPrice_xpath = ''
    self.eventImagePath_xpath = ''
    self.allEvents = []
    self.pages = []


    #print "url: ", self.url
    #print "pagination: ", self.pagination
    #print "Site Type: " , repr(self.siteType)


  def SetObjects(self):  #May just individually define local variables that i'm using.
    pass

  def ParsePage(self):  #This is for parsing the whole page (where page includes pagination and all that other good stuffs)
    #We know there has to be a list.
    #First thing i'm going to do is get all the page links and put them into a URL array that i'll load and then parse
    #Second thing is to check if the pages are organized by links that point to a details page, or if all the details are in the list-view
    #If CompleteList, 
    #  then parse each list item into an event and store in an array
    #If InCompleteList, 
    #  then, for each list, get all the pointer links
    #  fill each page into an event and store in an array
    #Store the events array in a relational database

    #Step 1: Get all the pages
    #  TODO: Make sure that we handle case where there is no pagination
    #  TODO: getting double the number of pages b/c of repeats. must only select one block of pagination.
    if self.pagination_xpath != "none":
      self.Pagination()
    else: self.pages = [self.url]

    #confirm that links are grabbed:
    print self.pages
    


    #Step 2: Fork to check style of the events-list
    if self.siteType == SiteTypes.ListEvents:
      print "This is a List of Events"

    elif self.siteType == SiteTypes.ListLinks:
      print "This in a List of Links to Event Landing Pages"
      eventLinks = self.GetLinkToEventDetails() #Get all the event Links from every single page
      print "Num Event Links: ", len(eventLinks)
      i = 1
      for eventLink in eventLinks:
        self.allEvents.append(self.GetSingleEvent(eventLink)) #For each event page, parse the page and get all the event details i can find.
        if i%25 == 0 or i == len(eventLinks):
          print "Printed Page: ", i
        i+=1
        #if i==10:
        #  print "breaking"
        #  break
    else:
      print "Something went wrong getting the SiteType"


  def GetLinkToEventDetails(self):
    links = []
    i=0
    for pageURL in self.pages:
      print "Getting Event Links page: " + str(i)
      pageURL = self.urlify(pageURL)

      self.page = requests.get(pageURL)
      thisTree = html.fromstring(self.page.text)
      links += thisTree.xpath(self.eventDetailsPageLink_xpath)
      print "finished event page links: " + str(i)
      i+=1
    links = set(links)
    return links

  def GetSingleEvent(self, eventLandingPage):
    eventLandingPage = self.urlify(eventLandingPage)

    self.page = requests.get(eventLandingPage)
    eventTree = html.fromstring(self.page.text)

    new_event = Event()
    new_event.source = eventLandingPage.encode('utf-8')
    new_event.name = self.multipleXPaths(self.eventName_xpath, eventTree, 'name')
    new_event.location += self.multipleXPaths(self.eventLocation_xpath, eventTree, 'location')
    new_event.description = self.multipleXPaths(self.eventDescription_xpath, eventTree, 'description')
    new_event.datetime  = self.multipleXPaths(self.eventDateTime_xpath, eventTree, 'datetime')
    new_event.price = self.multipleXPaths(self.eventPrice_xpath, eventTree, 'price')
    new_event.imagePath = self.multipleXPaths(self.eventImage_xpath, eventTree, 'imagePath')
    new_event.imagePath = self.urlify(new_event.imagePath)
    new_event.dump = SiteText(eventLandingPage).gettext()

    new_event.cleanContent()


    # print (new_event)
    # print (new_event.name), "             name"
    # print (new_event.location), "             location"
    # print (new_event.description), "             description"
    # print (new_event.datetime), "             datetime"  
    # print (new_event.price), "             price"
    # print (new_event.imagePath), "             imagePath"


    return new_event

  def multipleXPaths(self, xpath_array, pagetree, action):
    output = []
    if isinstance(xpath_array, list):
      for apath in xpath_array:
        hold = pagetree.xpath(apath)
        output.append(self.returnString(hold,action))
      outputStr = ",".join(output)
    else:
      outputStr = self.returnString(pagetree.xpath(xpath_array), action)
    return outputStr

  def urlify(self, sent_url):
    if sent_url.startswith("http://") is not True:
      if sent_url.startswith("./") or sent_url.startswith("~/"):
        sent_url = sent_url[1:]
      full_url = self.domain + sent_url
    else:
      full_url = sent_url

    return full_url

  def Pagination(self):
    if self.paginationType == PaginationTypes.AllPages:
      home = self.url
      self.page = requests.get(home)

      tree = html.fromstring(self.page.text)
      tree = tree.getroottree()
      print tree
      #grab all the links in a page.
      print self.pagination_xpath
      self.pages = tree.xpath(self.pagination_xpath)
      self.pages.insert(0,home)
      print "Num Pages: " + str(len(self.pages))
    
    elif self.paginationType == PaginationTypes.NextPage:
      nextPage = self.url.strip()
      while nextPage:
        nextPage = self.urlify(nextPage)
        print "next page: " + nextPage
        self.pages.append(nextPage)
        self.page = requests.get(nextPage)
        if self.page.status_code == 200:
          tree = html.fromstring(self.page.text)
          nextPage = tree.xpath(self.pagination_xpath)
        else:
          print "fuck! that didn't work:"
          print nextPage
          print self.page.status_code

    #dedupe pages
    self.pages = list(set(self.pages))

  def returnString(self, sentArray, action):
    sendable = []
    if isinstance(sentArray, list):
      if len(sentArray)>0:
        for item in sentArray:
          item = item.encode('utf-8').strip()
          sendable.append(item)
        return ("\n".join(sendable)).strip()
      else: return ""
    else:
      return str(sentArray).strip()


  def cleanParameters(self):
    self.url = self.stringify(self.url)
    self.domain = self.stringify(self.domain)
    self.siteType = self.stringify(self.siteType)
    self.pagination_xpath = self.stringify(self.pagination_xpath)
    self.paginationType = self.stringify(self.paginationType)
    self.eventDetailsPageLink_xpath = self.stringify(self.eventDetailsPageLink_xpath)
    self.eventName_xpath = self.stringify(self.eventName_xpath)
    self.eventLocation_xpath = self.stringify(self.eventLocation_xpath)
    self.eventDateTime_xpath = self.stringify(self.eventDateTime_xpath)
    self.eventDescription_xpath = self.stringify(self.eventDescription_xpath)
    self.eventPrice_xpath = self.stringify(self.eventPrice_xpath)
    self.eventImagePath_xpath = self.stringify(self.eventImagePath_xpath)

  def stringify(self, sentObj):
    if type(sentObj) is None:
      return ""
    elif type(sentObj) is str:
      return sentObj.encode("utf-8").strip()
    elif type(sentObj) is unicode:
      return str(sentObj).encode("utf-8").strip()
    elif type(sentObj) is list:
      for obj in sentObj:
        obj = self.stringify(obj)
      return sentObj
    else:
      return sentObj


  # def returnString(self, sentArray):
  #   sendable = ""
  #   if isinstance(sentArray, list):
  #     if len(sentArray)>0 : 
  #       for item in sentArray:
  #         hold = item.encode('utf-8').strip()
  #         if hold is not "": sendable = sendable + hold + ","
  #       return sendable[:-2]
  #     else: return ""
  #   else:
  #     return sentArray.strip()
