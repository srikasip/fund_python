#!/usr/bin/python3
#this is to test the scraping of a website

from lxml import html
import requests
import domstruct
from event_scraper import EventScraper
from enumerators import SiteTypes
from enumerators import PaginationTypes
from jsonScraper import JsonScraper
import json
import os

def main():
  #dom = domstruct.DomStruct('http://econpy.pythonanywhere.com/ex/001.html')
  #dom.Find()
  allOutput_js_fn = "EventsOutput/allOutput.json"
  allOutput_fn = "EventsOutput/allOutput.csv"
  allOutputTable_fn = "EventsOutput/allOutput.html"
  
  silentRemove(allOutput_js_fn)
  silentRemove(allOutput_fn)
  silentRemove(allOutputTable_fn)

  allOutput_js = open(allOutput_js_fn, 'w')
  allOutput = open(allOutput_fn, 'w')
  allOutputTable = open(allOutputTable_fn, 'w')

  allOutput.write('EventName\t EventLocation\t EventDateTime\t EventPrice\t EventDescription\t EventImage\n')
  allOutputTable.write("<html><head></head><body><table><tr><th>EventName</th><th>EventLocation</th><th>EventDateTime</th><th>EventPrice</th><th>EventDescription</th><th>EventImage</th></tr>\n")
  allOutput_js.write('{\n\t"event":[\n\t')


  with open('parsingXPaths.json') as data_file:    
    xpaths = json.load(data_file)

  for parser in xpaths["parsers"]:
    if parser["is_json"] == "true":
      link = parser["link"]
      name = parser["name"]
      param = parser["pageVar"]
      scraper = JsonScraper(link, name, param)
      scraper.eventResults = parser["eventResult"]
      scraper.eventName = parser["eventName"]
      scraper.description = parser["description"]
      scraper.eventTime = parser["eventTime"]
      scraper.image = parser["image"]
      scraper.location = parser["location"]
      scraper.price = parser["price"]

      scraper.parse()

    else:
      link = parser["link"]
      pagination = parser["pagination"]
      siteType = SiteTypes(int(parser["site_type"]))
      paginationType = PaginationTypes(int(parser["pagination_type"]))
      scraper = EventScraper(link, SiteTypes.ListLinks, pagination, paginationType)

      scraper.domain = parser["domain"]
      scraper.eventDetailsPageLink_xpath = parser["eventDetailsPageLink_xpath"]
      scraper.eventName_xpath = parser["eventName_xpath"]
      scraper.eventLocation_xpath = parser["eventLocation_xpath"]
      scraper.eventDateTime_xpath = parser["eventDateTime_xpath"]
      scraper.eventDescription_xpath = parser["eventDescription_xpath"]
      scraper.eventPrice_xpath = parser["eventPrice_xpath"]
      scraper.eventImage_xpath = parser["eventImage_xpath"]

      scraper.cleanParameters()
      scraper.ParsePage()


    
    fileData = "EventsOutput/{}.csv".format(parser['name'])
    fileHtml = "EventsOutput/{}.html".format(parser['name'])

    silentRemove(fileData)
    silentRemove(fileHtml)

    eventsData = open(fileData, 'w')
    eventsTable = open(fileHtml, 'w')

    tablestr = "<html><head></head><body><table><tr><th>EventName</th><th>EventLocation</th><th>EventDateTime</th><th>EventPrice</th><th>EventDescription</th><th>EventImage</th></tr>\n"
    eventstr = 'EventName\t EventLocation\t EventDateTime\t EventPrice\t EventDescription\t EventImage\n'
    eventsData.write(eventstr)
    eventsTable.write(tablestr)


    for event in scraper.allEvents:
      eventstr = '{}\t {}\t {}\t {}\t {}\t {}\n'.format(event.name, event.location, event.datetime, event.price, event.description, event.imagePath)
      allOutput.write(eventstr)
      eventsData.write(eventstr)

      tablestr = '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>\n'.format(event.name, event.location, event.datetime, event.price, event.description, event.imagePath)
      eventsTable.write(tablestr)
      allOutputTable.write(tablestr)
      allOutput_js.write(event.writeJSON() + ",\n\t")

    
       
    tablestr = "</table></body></html>"
    eventsTable.write(tablestr)

    eventsData.close() 
    eventsTable.close()

  allOutputTable.write("</table></body></html>")
  
  allOutput_js.close()

  with open(allOutput_js_fn, 'rb+') as filehandle:
    filehandle.seek(-3, os.SEEK_END)
    filehandle.truncate()

  allOutput_js = open(allOutput_js_fn, 'a')
  allOutput_js.write('\n\t]\n}')
  allOutput_js.close()

  allOutput.close()
  allOutputTable.close()

def silentRemove(filename):
  try:
    os.remove(filename)
  except OSError:
    pass

def getStuff():
  buyers = []
  prices = []

  home = 'http://econpy.pythonanywhere.com/ex/001.html'
  page = requests.get(home)
  tree = html.fromstring(page.text)

  #grab all the links in a page.
  links = tree.xpath('//a/@href')
  links.insert(0,home)


  for link in links:
    page = requests.get(link)
    tree = html.fromstring(page.text)

    #This will append to the list of buyers:
    buyers += tree.xpath('//div[@title="buyer-name"]/text()')
    #This will append to the list of prices
    prices += tree.xpath('//span[@class="item-price"]/text()')

  print 'Links: ', links
  print 'Buyers: ', buyers
  print "Prices: ", prices

if __name__ == "__main__": main()


