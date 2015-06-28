#!/usr/bin/python3
#this is to define class 

from lxml import html
import requests

class DomStruct:
  def __init__(self, url = 'http://www.google.com'):
    self.page = requests.get(url)
    self.tree = html.fromstring(self.page.text)

    for i in self.tree.xpath('/*/*/*'): print (i.tag)

  def Find(self, searchString):
    childrenElems = self.tree.xpath(searchString + '/*')
    self.children = []

    for child in childrenElems:
      self.children.append(child.tag)

    return self.children
