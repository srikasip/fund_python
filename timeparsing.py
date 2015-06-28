import re
from pprint import pprint

class TimeParser:
  def __init__(self, allEvents = [], objNameWaterfall = []):
    objName = "datetime"
    self.events = allEvents
    self.objNameWaterfall = objNameWaterfall
    self.objName = objName
    self.repTime = self.setRegex()
    


  def doParse(self):
    times = []
    hasTimes = 0
    noTimes = 0
    for event in self.events:
      times = []
      for objName in self.objNameWaterfall:
        times.extend(self.cleanTime(event[objName].replace("\\n","\n").replace("\\r", "\r").replace("\\t", "\t")))

      event["time"] = times
      if len(times)>0:
        hasTimes += 1
      else:
        noTimes += 1


    print "-------------------------------------\n\r"
    print "Total Num Events: " + str(hasTimes+noTimes)
    print "Non-empty Times: " + str(hasTimes)
    print "Empty Times: " + str(noTimes)

    return self.events

  def cleanTime(self, searchString):
    a = [0,0,0,0]
    times = []
    miter = list(self.repTime.finditer(searchString))

    #a[0] = len(miter)

    if len(miter)>0:
      for m in miter:
        times.append(m.group())

    #print str.format("a: {}, b: {}, c:{}, d:{}",*a)
    return times


  def setRegex(self):
    #(\d+(am|pm|:)?(-|\sto\s))?\d+[:]?\d*(am|pm|:)\d*
    #
    #p = re.compile(r'(\d+\s*(am|pm|:)*\s*\d*)(\s*(-|to)\s*)*(\d+[:]?\d*\s*(am|pm|:)\d*)*', re.IGNORECASE)
    #p = re.compile(r'(\d+\s*(am|pm|:)?\s*(-|to)\s*)?\d+[:]?\d*\s*(am|pm|:)\d*', re.IGNORECASE)
    p = re.compile(r'(\b\d{1,2}\s*(:\d\d)*\s*(to|-)\s*)*((\d+)\s*(a\.*m\.*|p\.*m\.*|(:\s*\d+\s*(a\.*m\.*|p\.*m\.*|(:\s*\d+\s*(a\.*m\.*|p\.*m\.*)*)))))', re.IGNORECASE)

    return p

  def arrayToOr(self, sentArray):
    sentArray = [item.replace(' ', '[\\s\\r\\t\\n]*') for item in sentArray]
    joinStr = "|".join(sentArray)
    joinStr = "("+joinStr+")"
    return joinStr
