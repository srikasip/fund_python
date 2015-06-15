import json
import urllib
from bs4 import BeautifulSoup
import bs4
import re

class SiteText:
  def __init__(self, sentUrl = "http://www.google.com"):
    self.url = sentUrl;
    self.siteText = ""

  def gettext(self):
    html = urllib.urlopen(self.url).read()
    soup = BeautifulSoup(html)
    texts = soup.findAll(text=True)
    visible_text_elems = filter(self.visible, texts)
    returnStr = ""

    for text_elem in visible_text_elems:
      if text_elem.parent.name in ["div", "p", "li"]:
        returnStr += "\n" + unicode(text_elem).replace("\t", " ").strip()
      elif text_elem.parent.name == "td":
        if list(text_elem.parent.parent.children)[0] == text_elem.parent:
          returnStr += "\n" + unicode(text_elem).replace("\t", " ").strip()
        else:
          returnStr += "\t" + unicode(text_elem).replace("\t", " ").strip()
      elif text_elem.parent.name in ["span", "a", "strong", "i", "b"]:
        returnStr += " " + unicode(text_elem).replace("\t", " ").strip()
      else:
        returnStr += " " + unicode(text_elem).replace("\t", " ").strip()

      
    return returnStr.encode('utf-8').replace('"', "'").strip()

  def visible(self, element):
    if type(element) != bs4.element.NavigableString:
      return False
    elif element.parent.name in ['style', 'script', '[document]', 'head', 'title', 'option', 'select', 'input', 'textarea', 'button', 'form']:
      return False
    elif (unicode(element).strip() == None) or (unicode(element).strip() == ""):
      return False

    #print element.parent.name
    return True