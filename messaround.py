import requests
from lxml import html
import json
import os
import pyap
from pprint import pprint
import urllib
from bs4 import BeautifulSoup
import bs4
import re
#import requests

def main():
  with open('EventsOutput/allProcessedData.json') as data_file:    
    jsObj = json.load(data_file)
  pprint(jsObj)

def visible(element):
  if type(element) != bs4.element.NavigableString:
    return False
  elif element.parent.name in ['style', 'script', '[document]', 'head', 'title', 'option', 'select', 'input', 'textarea', 'button', 'form']:
    return False
  elif (unicode(element).strip() == None) or (unicode(element).strip() == ""):
    return False

  #print element.parent.name
  return True



if __name__ == "__main__": main()