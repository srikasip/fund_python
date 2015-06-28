import re
from pprint import pprint

class PriceParser:
  def __init__(self, allEvents = [], objNameWaterfall = []):
    objName = "price"
    self.events = allEvents
    self.objNameWaterfall = objNameWaterfall
    self.objName = objName
    self.repPrice = self.setRegex()


  def doParse(self):
    prices = []
    hasPrice = 0
    noPrice = 0
    for event in self.events:
      prices = []
      for objName in self.objNameWaterfall:
        prices.extend(self.cleanPrice(event[objName].replace("\\n","\n").replace("\\r", "\r").replace("\\t", "\t")))

      event["pPrice"] = prices
      #print event["datetime"]
      #print event["time"]
      if len(prices)>0:
        hasPrice += 1
      else:
        noPrice += 1

    print "-------------------------------------\n\r"
    print "Total Num Events: " + str(hasPrice+noPrice)
    print "Non-empty Prices: " + str(hasPrice)
    print "Empty Prices: " + str(noPrice)

    return self.events

  def cleanPrice(self, searchString):
    a = [0,0,0,0]
    prices = []
    miter = list(self.repPrice.finditer(searchString))

    #a[0] = len(miter)

    if len(miter)>0:
      for m in miter:
        prices.append(m.group())

    #print str.format("a: {}, b: {}, c:{}, d:{}",*a)
    return prices

  def setRegex(self):
    #(\d+(am|pm|:)?(-|\sto\s))?\d+[:]?\d*(am|pm|:)\d*
    #
    #p = re.compile(r'(\d+\s*(am|pm|:)*\s*\d*)(\s*(-|to)\s*)*(\d+[:]?\d*\s*(am|pm|:)\d*)*', re.IGNORECASE)
    #p = re.compile(r'(\d+\s*(am|pm|:)?\s*(-|to)\s*)?\d+[:]?\d*\s*(am|pm|:)\d*', re.IGNORECASE)

    p = re.compile(r'(((\$\s*\d+(\.\d+)*)(\s*(-|to)\s*(\$\s*\d+(\.\d*)))*)|free)', re.IGNORECASE)

    return p

  def arrayToOr(self, sentArray):
    sentArray = [item.replace(' ', '[\\s\\r\\t\\n]*') for item in sentArray]
    joinStr = "|".join(sentArray)
    joinStr = "("+joinStr+")"
    return joinStr
