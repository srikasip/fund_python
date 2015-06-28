import re
from pprint import pprint

class DateParser:
  def __init__(self, allEvents = [], objNameWaterfall = []):
    self.events = allEvents
    self.objNameWaterfall = objNameWaterfall
    
    self.repLongString = self.setLongStringRegex()
    self.repLongNum = self.setMDYregex()
    self.repYMDNum = self.setYMDregex()
    self.repShortNum = self.setMDregex()

  def doParse(self):
    hasDates = 0
    noDates = 0
    for event in self.events:
      dates = []
      for objName in self.objNameWaterfall:
        dates = self.cleanDate(event[objName].replace("\\n","\n").replace("\\r", "\r").replace("\\t", "\t"))
        if len(dates)>0:
          break;

      event["date"] = []
      for date in dates:
        event["date"].append(date["dateString"])
      
      event["date_match"] = dates

      #event["date"] = dates
      if len(dates)>0:
        hasDates += 1
      else:
        noDates += 1

    #self.cleanDuplicates()

    print "-------------------------------------\n\r"
    print "Total Num Events: " + str(hasDates+noDates)
    print "Non-empty Dates: " + str(hasDates)
    print "Empty Dates: " + str(noDates)

    return self.events

  def cleanDate(self, searchString):
    a = [0,0,0,0]
    dates = []
    miter = list(self.repLongString.finditer(searchString))
    dateType = "longString"
    #a[0] = len(miter)

    if len(miter)<1:
       miter = list(self.repLongNum.finditer(searchString))
       dateType = "MDYNum"
       #a[1] = len(miter)
    if len(miter)<1:
      miter = list(self.repYMDNum.finditer(searchString))
      dateType = "YMDNum"
      #a[2] = len(miter)
    if len(miter)<1:
      miter = list(self.repShortNum.finditer(searchString))
      dateType = "MDNum"
      #a[3] = len(miter)

    if len(miter)>0:
      for m in miter:
        dateObj = {"dateString":m.group(), "start":m.start(), "end":m.end(), "dateType":dateType}
        dates.append(dateObj)

    #print str.format("a: {}, b: {}, c:{}, d:{}",*a)
    return dates


  def cleanDuplicates(self):
    for event in self.events:
      for date in event["date"]:
        date = date.replace(" ,", ",")




  def setLongStringRegex(self):
    month_words = ["january","february","march","april","may","june","july","august","september","october","november","december","jan","feb","mar","apr","may","jun","jul","aug","sept", "sep","oct","nov","dec"]
    month_nums = ["1","2","3","4","5","6","7","8","9","10","11","12","01","02","03","04","05","06","07","08","09"]
    numWeek = ["first", "second", "third", "fourth", "1 st", "2 nd", "3 rd", "4 th"]
    firstFriLink = ["of the month", "of", "for", "in", "the"]
    weekdays = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sun", "mon", "tue", "wed", "thu", "fri", "sat"]
    days = ["01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31","1","2","3","4","5","6","7","8","9"]
    years = ["2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020","2021","2022"]
    stopWords = [" the ", " of ", "  ", "  "]
    numEndings = ["th", "st", "nd", "rd"]
    specialChars = ["\"", "'", ",", ".", "|", "-"]
    linkingWords = ["-","to the", "through the","to", "through"]


    reMonth = self.arrayToOr(month_words)
    reDays = self.arrayToOr(days)
    reYears = self.arrayToOr(years)
    reNumEndings = self.arrayToOr(numEndings)
    reLinkingWords = self.arrayToOr(linkingWords)
    reNumWeek = self.arrayToOr(numWeek)
    reWeekday = self.arrayToOr(weekdays)
    reFirstFriLink = self.arrayToOr(firstFriLink)


    searchQuery = "\\b([\\(]*"+reNumWeek+"*\s*"+reWeekday+"*\s*"+reFirstFriLink+"*[,\\)]*\s*"+reMonth+"[\\s\\.]*"+reDays+"*"+reNumEndings+"*[\\s,]*"+reYears+"*)([\\s\\t\\n\\r]+[\\(]*"+reLinkingWords+"\\s*"+reWeekday+"*\s*"+reFirstFriLink+"*[,\\)]*\s*"+reMonth+"*\\s*"+reDays+"*\\s*"+reNumEndings+"*)*\\b"

    #print searchQuery

    return re.compile(searchQuery, re.IGNORECASE)

  def setMDYregex(self):
    month_nums = ["01","02","03","04","05","06","07","08","09","10","11","12","1","2","3","4","5","6","7","8","9"]
    days = ["01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31","1","2","3","4","5","6","7","8","9"]
    years = ["2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020","2021","2022", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22"]

    reMonth = self.arrayToOr(month_nums)
    reDay = self.arrayToOr(days)
    reYear = self.arrayToOr(years)

    searchQuery = "\\b"+reMonth+"[/-]"+reDay+"[/-]*"+reYear+"*\\b"

    print "MDY Regex: " + searchQuery
    return re.compile(searchQuery, re.IGNORECASE)

  def setYMDregex(self):
    month_nums = ["01","02","03","04","05","06","07","08","09","10","11","12","1","2","3","4","5","6","7","8","9"]
    days = ["01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31","1","2","3","4","5","6","7","8","9"]
    years = ["2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020","2021","2022", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22"]

    reMonth = self.arrayToOr(month_nums)
    reDay = self.arrayToOr(days)
    reYear = self.arrayToOr(years)

    searchQuery = "\\b"+reYear+"[/-]"+reMonth+"[/-]"+reDay+"\\b"

    print "YMD Regex: " + searchQuery
    return re.compile(searchQuery, re.IGNORECASE)


  def setMDregex(self):
    month_nums = ["01","02","03","04","05","06","07","08","09","10","11","12","1","2","3","4","5","6","7","8","9"]
    days = ["01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31","1","2","3","4","5","6","7","8","9"]
    years = ["2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020","2021","2022", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22"]

    reMonth = self.arrayToOr(month_nums)
    reDay = self.arrayToOr(days)
    reYear = self.arrayToOr(years)

    searchQuery = "\\b"+reMonth+"[/-]"+reDay+"\\b"

    print "MD Regex: " + searchQuery
    return re.compile(searchQuery, re.IGNORECASE)


  def arrayToOr(self, sentArray):
    sentArray = [item.replace(' ', '[\\s\\r\\t\\n]*') for item in sentArray]
    joinStr = "|".join(sentArray)
    joinStr = "("+joinStr+")"
    return joinStr
