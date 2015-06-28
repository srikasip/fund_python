import re
from pprint import pprint
import json

class ProximityParser:
  def __init__(self, allEvents = [], objNameWaterfall = []):
    self.events = allEvents
    self.objNameWaterfall = objNameWaterfall
    
    self.repLongString = self.setLongStringRegex()
    self.repLongNum = self.setMDYregex()
    self.repYMDNum = self.setYMDregex()
    self.repShortNum = self.setMDregex()
    self.repTime = self.setTimeRegex()

    with open('month_variants.json') as output_file:
      monthHolder = json.load(output_file)

    self.month_variants = monthHolder["months"]


  def LinkDateToTime(self):
    newEvent = {}
    allEvents = []
    for event in self.events:
      if len(event["date_objects"]) == 0:
        pass #remove anything that doesn't have a date
      elif len(event["date_objects"]) == 1:
        newEvent = event
        newEvent["datetime_structs"] = []
        if len(event["time_structs"])>0:
          for time in event["time_structs"]:
            obj = {"date":event["date_objects"][0], "time":time}
            newEvent["datetime_structs"].append(obj)
          allEvents.append(newEvent)
      else:
        if len(event["time_structs"]) == 0:
          pass #remove anything that does not have a time
        elif len(event["time_structs"]) == 1:
          newEvent = event
          newEvent["datetime_structs"] = []
          if len(event["date_objects"])>0:
            for date in event["date_objects"]:
              obj = {"date":date, "time":event["time_structs"][0]}
              newEvent["datetime_structs"].append(obj)
            allEvents.append(newEvent)
        else:
          newEvent = event
          newEvent["datetime_structs"] = self.CollateDatesAndTimes(event)
          allEvents.append(newEvent)

    self.events = allEvents

    hasDates = 0
    noDates = 0
    for event in self.events:
      if len(event["datetime_structs"])>0:
        hasDates += 1 
      else:
        noDates += 1


    print "-------------------------------------\n\r"
    print "Total Num Events: " + str(hasDates+noDates)
    print "Non-empty DateTime Object: " + str(hasDates)
    print "Empty DateTime Object: " + str(noDates)


    return self.events

    # for event in self.events:
    #   # print event["date_objects"]
    #   # print event["time_structs"]
    #   for date in event["date_objects"]:
    #     if date.get("original_match"):
    #       for time in event["time_structs"]:
    #         if time.get("original_string"):



  def CollateDatesAndTimes(self, event):
    dates = event["date_objects"]
    times = event["time_structs"]
    distances = []
    datetime_structs = []
    #get the distance between every time and date block.
    for date in dates:
      distance = []
      for time in times:
        if date["original_match"]["start"] < time["time_match"]["start"]:
          d = time["time_match"]["start"] - date["original_match"]["end"]
        else:
          d = date["original_match"]["start"] - time["time_match"]["end"]
        distance.append(d)
      distances.append(distance)

    for distance in distances:
      minValue = min(distance)
      timeIndex = distance.index(minValue)
      dateIndex = distances.index(distance)
      datetime = {"date":dates[dateIndex], "time":times[timeIndex]}
      datetime_structs.append(datetime)

    return datetime_structs



  def LinkDates(self):
    for event in self.events:
      # go through an event and get the date_match object
      # send the datetime object to a place so that it can be canonicalized. 
      #Then go to link dates to times.
      event["date_objects"] = []
      for date_match in event["date_match"]:
        hold = self.getDateObject(date_match)
        if hold and hold != {}:
          event["date_objects"].append(hold)


    hasDates = 0
    noDates = 0
    for event in self.events:
      if event.get("date_objects") and len(event["date_objects"])>0:
        hasDates += 1
      else:
        #pprint(event["date_match"])
        noDates += 1

    print "-------------------------------------\n\r"
    print "Total Num Events: " + str(hasDates+noDates)
    print "Non-empty Dates w/ Structure: " + str(hasDates)
    print "Empty Dates w/ Structure: " + str(noDates)

    return self.events

  def getDateObject(self, date_match):
    #break the date into two dateStrings
    linkingWords = ["\b-\b","to the", "through the","\\bto\\b", "\\bthrough\\b"]
    reLinkWords = self.arrayToOr(linkingWords)
    reLinkWords = reLinkWords.replace("(", "").replace(")","")
    dateString = date_match["dateString"]
    dateParts = [x for x in re.split(reLinkWords, dateString) if (x and x!= "")]
    procDates = []
    returnDateObj = {}
    valid_months = [ a_month["name"] for a_month in self.month_variants ]
    #print valid_months
    for date in dateParts:
      myDate = self.canonicalizeDate(date, date_match["dateType"])
      #print myDate

      if myDate.get("status")=="success" and myDate["day"]>0 and myDate.get("month") in valid_months:
        procDates.append(myDate)

    if len(procDates) == 1:
      if procDates[0]["year"] == 0:
        procDates[0]["year"] = 2015
        procDates[0]["year_string"] = "2015"
    elif len(procDates) == 2:
      if procDates[0]["year"] == 0:
        if procDates[1]["year"] == 0:
          procDates[0]["year"] = 2015
          procDates[0]["year_string"] = "2015"
          procDates[1]["year"] = 2015
          procDates[1]["year_string"] = "2015"
        else:
          procDates[0]["year"] = procDates[1]["year"]
          procDates[0]["year_string"] = procDates[1]["year_string"]
      
      if procDates[1]["year"] == 0:
        procDates[1]["year"] = procDates[0]["year"]
        procDates[1]["year_string"] = procDates[0]["year_string"]


    for ddate in procDates:
      ddate["full_date"] = ddate["month"]+", " + ddate["day_string"] + " " + ddate["year_string"]

    if len(procDates) == 1:
      returnDateObj = {"start_date":procDates[0], "original_match":date_match}
    elif len(procDates) == 2:
      returnDateObj = {"start_date":procDates[0], "end_date":procDates[1], "original_match":date_match}


    # pprint(date_match)
    # pprint(procDates)


    # print "-------------"
    # print date_match["dateString"]
    # pprint(returnDateObj)

    return returnDateObj



  def canonicalizeDate(self, sentDate, dateType):
  #assume that this contains the words.
    #clean the dateString, but dont mess with the original.
    dateString = sentDate.replace("\\n", "").replace("\\r", "").replace("\\t", "").replace(",", " ")
    dateString = dateString.replace("  ", " ").replace("  ", " ")
    dateString = dateString.strip()
    dateString = dateString.lower()

    #TODO: extend getMonth to include numbered months of all types
    if dateType == "longString":
      month = self.getMonth(dateString, dateType)
      day = self.getDay(dateString, dateType)
      year = self.getYear(dateString, dateType)
    elif dateType == "MDYNum":
      dateParts = self.numberedDate(dateString)
      if len(dateParts)>1:
        month_index = dateParts[0]-1
        if month_index < 12:
          month = self.month_variants[month_index]["name"]
        else:
          month = "error"
        day = dateParts[1]
      if len(dateParts)>=3:
        year = dateParts[2]
      else:
        year = 2015
    elif dateType == "YMDNum":
      dateParts = self.numberedDate(dateString)
      if len(dateParts)>=3:
        month_index = dateParts[1]-1
        if month_index < 12:
          month = self.month_variants[month_index]["name"]
        else:
          month = "error"
        day = dateParts[2]
        year = dateParts[0]
    elif dateType == "MDNum":
      dateParts = self.numberedDate(dateString)
      if len(dateParts)>1:
        month_index = dateParts[0]-1
        if month_index < 12:
          month = self.month_variants[month_index]["name"]
        else:
          month = "error"
        day = dateParts[1]
        year = 2015
    else:
      month = "error"
      day = 0
      year = 0


    if day and month and day != 0 and month != "error":
      canonDate = month + " " + self.twodigitNum(day) + ", " + str(year)
      date = {"status":"success","full_date":canonDate, "month":month, "day":day, "year":year, "day_string":self.twodigitNum(day), "year_string":str(year)}
    else:
      date = {"status":"error", "day":0}
    
    return date



  def numberedDate(self, fullDate):
    dateString = fullDate.lower()
    dateParts = [x for x in re.split("-|/", dateString) if (x and x!= "")]
    linkingWords = ["st", "nd", "rd", "th"]
    #strip each datePart and make sure that each one is a number:
    p = re.compile("\\d+", re.IGNORECASE)
    returnInts = []
    for part in dateParts:
      part = part.strip()
      for link in linkingWords:
        part = part.replace(link, "")
      match = p.search(part)
      if match:
        intify = self.intConvert(match.group())
        returnInts.append(intify)

    return returnInts



  def getMonth(self, fullDate, dateType):
    dateString = fullDate.lower()
    month_words = ["january","february","march","april","may","june","july","august","september","october","november","december","jan","feb","mar","apr","may","jun","jul","aug","sept", "sep","oct","nov","dec"]
    reMonths = self.arrayToOr(month_words)
    holdMonth = "error"

    #longString, MDYNum, YMDNum, MDNum
    if dateType == "longString":
      p = re.compile(reMonths, re.IGNORECASE)
      m = p.search(dateString)
      if m:
        string_month = m.group()
        for month in self.month_variants:
          if string_month in month["variants"]:
            holdMonth = month["name"]
            break
      
    return holdMonth


  def getDay(self, fullDate, dateType):
    dateString = fullDate.lower()
    month_words = ["january","february","march","april","may","june","july","august","september","october","november","december","jan","feb","mar","apr","may","jun","jul","aug","sept", "sep","oct","nov","dec"]
    linkingWords = ["st", "nd", "rd", "th"]
    reLink = self.arrayToOr(linkingWords)
    reMonths = self.arrayToOr(month_words)

    holdDay = "00"
    day = 0
    if dateType == "longString":
      p = re.compile(reMonths+"\\s*\\d{1,2}"+reLink+"*\\b", re.IGNORECASE)
      m = p.search(dateString)
      if m:
        holdDay = m.group()
        for month in month_words:
          holdDay = holdDay.replace(month, "")
        for link in linkingWords:
          holdDay = holdDay.replace(link, "")
        holdDay = holdDay.strip()
        day = self.intConvert(holdDay)
        if day>31:
          day = 0

    return day

  def getYear(self, fullDate, dateType):
    dateString = fullDate.lower()
    month_words = ["january","february","march","april","may","june","july","august","september","october","november","december","jan","feb","mar","apr","may","jun","jul","aug","sept", "sep","oct","nov","dec"]
    linkingWords = ["st", "nd", "rd", "th"]
    reLink = self.arrayToOr(linkingWords)
    reMonths = self.arrayToOr(month_words)

    holdDay = "00"
    day = 0
    year = 0
    
    if dateType == "longString":
      p = re.compile(reMonths+"\\s*\\d{1,2}"+reLink+"*\\b", re.IGNORECASE)
      m = p.search(dateString)
      year = 0
      if m:
        end = m.end() + 1
        if end >= len(dateString):
          year = 0
        else:
          yearStr = dateString[end:]
          year = self.intConvert(yearStr)

    if 0<year<=20:
      year = 2000+year
    elif year>=3000:
      year = 0

    return year



  def LinkTimes(self):
    #easiest case first. all the dates and times are 
    for event in self.events:
      wholeEventTimes = []
      for objName in self.objNameWaterfall:
        searchString = self.readableLongJSON(event[objName])
        timeMatches = list(self.repTime.finditer(searchString))
        numMatches = len(timeMatches)
        eventTimes = []
        #print event["name"] + "\n"+ objName
        #print numMatches
        if numMatches>1:
          for i in range(numMatches-1):
            eventTimes.extend(self.timesLinked(timeMatches[i], timeMatches[i+1], searchString))

        elif numMatches == 1:
          timeData = self.canonicalizeTime(timeMatches[0].group(), timeMatches[0])
          if timeData.get("is_success") == "true":
            eventTimes = [timeData]
          else:
            eventTimes = []

        eventTimes = self.cleanEventStruct(eventTimes)
        eventTimes = self.cleanEventStruct(eventTimes)
        wholeEventTimes.extend(eventTimes)

      event["time_structs"] = wholeEventTimes

    hasTimes = 0
    noTimes = 0
    for event in self.events:
      if len(event["time_structs"])>0:
        hasTimes += 1
      else:
        noTimes += 1

    print "-------------------------------------\n\r"
    print "Total Num Events: " + str(hasTimes+noTimes)
    print "Non-empty Times Struct: " + str(hasTimes)
    print "Empty Times Struct: " + str(noTimes)
    

    return self.events

  def cleanEventStruct(self, eventTimes):
    finalAnswer = []
    for i in range(len(eventTimes)-1):
      if eventTimes[i].get("start_time") == eventTimes[i+1].get("start_time"):
        finalAnswer.append(eventTimes[i+1])
      elif len(finalAnswer)>0 and finalAnswer[len(finalAnswer)-1].get("start_time") != eventTimes[i].get("start_time"):
        finalAnswer.append(eventTimes[i])
      else:
        finalAnswer.append(eventTimes[i])

    if len(finalAnswer)>0:
      if (eventTimes[len(eventTimes)-1].get("start_time") != finalAnswer[len(finalAnswer)-1].get("start_time")) and (eventTimes[len(eventTimes)-1].get("start_time") != finalAnswer[len(finalAnswer)-1].get("end_time")):
        finalAnswer.append(eventTimes[len(eventTimes)-1])
    elif len(eventTimes) >= 1:
      finalAnswer.append(eventTimes[len(eventTimes)-1])

    return finalAnswer

  def timesLinked(self, match1, match2, searchString):

    timeData1 = self.canonicalizeTime(match1.group(), match1)
    timeData2 = self.canonicalizeTime(match2.group(), match2)
    sendable = []

    if ((timeData1.get("is_success") == "true" and timeData1.get("end_time") is None) and (timeData2.get("is_success")=="true" and timeData2.get("end_time") is None)):
      startIndex = match1.end()+1
      endIndex = match2.start()

      betweenText = searchString[startIndex:endIndex]
      betweenText = betweenText.strip()

      
      if betweenText in ["to", "through", "-", "and ending at", "ending at", "->", "-->"]:
        origString = self.writableLongJSON(searchString[match1.start():(match2.end()+1)])
        #print self.canonicalizeTime(match1.group()) + "_to_" + self.canonicalizeTime(match2.group())
        sendable = [{"is_success":"true", "start_time":timeData1["start_time"], "end_time":timeData2["start_time"], "original_string":origString}]
        sendable[0]["time_match"] = {"timeString": origString, "start":match1.start(), "end":match2.end()}
      else:
        sendable = [timeData1, timeData2]


    else:
      if timeData1["is_success"] == "true":
        sendable = [timeData1]
      if timeData2["is_success"] == "true":
        sendable.append(timeData2)

    return sendable

  def canonicalizeTime(self, timeString, timeMatch):
    time = timeString
    time = time.replace(' ', '')
    time = time.lower()
    time = time.replace("a.m", "am").replace("p.m", "pm").replace("am.", "am").replace("pm.", "pm")
    
    if ("-" in time) or ("to" in time):
      sendTimeData = self.canonicalizeTimePairs(time)
      sendTimeData["original_string"] = self.writableLongJSON(timeString)
      if sendTimeData.get("is_success") == "true":
        sendTimeData["time_match"] = {"timeString": timeMatch.group(), "start": timeMatch.start(), "end":timeMatch.end()}
    else:
      sendTimeData = self.getTimeString(time)
      sendTimeData["original_string"] = self.writableLongJSON(timeString)
      if sendTimeData.get("is_success") == "true":
        sendTimeData["time_match"] = {"timeString": timeMatch.group(), "start": timeMatch.start(), "end":timeMatch.end()}

    return sendTimeData


  def canonicalizeTimePairs(self, time):
    if ("-" in time) or ("to" in time):
      times = [x for x in re.split("-|to", time) if (x and x!= "")]

      if len(times) == 2:
        secondTime = self.getTimeString(times[1])
        secondEnding = self.getAM_PM_FromString(times[1])
        firstTime = self.getTimeString(times[0], secondEnding)
        #11-2pm will produce 11pm-2pm, which doesn't at all make sense!
        if firstTime.get("is_success")!="false" and secondTime.get("is_success") != "false":
          data = {"is_success":"true", "start_time":firstTime["start_time"], "end_time":secondTime["start_time"]}
        else:
          data = {"is_success":"false"}
      else:
        data = {"is_success":"false"}
    else:
      data = {"is_success":"false"}

    return data


  def getTimeString(self, time, ending=""):
    sendData = {}

    if ending == "":
      ending = self.getAM_PM_FromString(time)

    timePart = time.replace(ending, "")

    newTimeString = ""
    timeParts = timePart.split(":")

    if len(timeParts) == 1:
      hold = self.getAM_PM(timeParts[0])
      newTimeString = str(hold["hour"]) + ":00" + ending
    elif len(timeParts) >= 2:
      hold = self.getAM_PM(timeParts[0])
      minutes = timeParts[1].strip()
      newTimeString = str(hold["hour"]) + ":"+minutes
      if ending != "":
        newTimeString = newTimeString + ending
      else:
        ending = hold["ampm"]
        newTimeString = newTimeString + hold["ampm"]
    else:
      newTimeString = "InvalidTime"
      sendData = {"is_success":"false"}

    if sendData.get("is_success") is None:
      sendData = {"is_success":"true", "start_time":newTimeString}

    return sendData

  def getAM_PM_FromString(self, time):
    index = time.find("am")
    if index<0:
      index = time.find("pm")
      ending = "pm"
    else:
      ending = "am"

    if index<0:
      ending = ""

    return ending

  def getAM_PM(self, hourDigits):
    hours = int(hourDigits)
    ampmHour = (hours%12)
    if hours<12:
      ampmHour = hours
      ending = "am"
    elif hours>12:
      ampmHour = hours - 12
      ending = "pm"
    else:
      ampmHour = hours
      ending = "pm"

    return {"hour": ampmHour, "ampm":ending}












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


  def setTimeRegex(self):
    #(\d+(am|pm|:)?(-|\sto\s))?\d+[:]?\d*(am|pm|:)\d*
    #
    #p = re.compile(r'(\d+\s*(am|pm|:)*\s*\d*)(\s*(-|to)\s*)*(\d+[:]?\d*\s*(am|pm|:)\d*)*', re.IGNORECASE)
    #p = re.compile(r'(\d+\s*(am|pm|:)?\s*(-|to)\s*)?\d+[:]?\d*\s*(am|pm|:)\d*', re.IGNORECASE)
    p = re.compile(r'(\b\d{1,2}\s*(:\d\d)*\s*(to|-)\s*)*((\d+)\s*(a\.*m\.*|p\.*m\.*|(:\s*\d+\s*(a\.*m\.*|p\.*m\.*|(:\s*\d+\s*(a\.*m\.*|p\.*m\.*)*)))))', re.IGNORECASE)

    return p

  def setMDYregex(self):
    month_nums = ["01","02","03","04","05","06","07","08","09","10","11","12","1","2","3","4","5","6","7","8","9"]
    days = ["01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31","1","2","3","4","5","6","7","8","9"]
    years = ["2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020","2021","2022", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22"]

    reMonth = self.arrayToOr(month_nums)
    reDay = self.arrayToOr(days)
    reYear = self.arrayToOr(years)

    searchQuery = "\\b"+reMonth+"[/-]"+reDay+"[/-]*"+reYear+"*\\b"

    #print "MDY Regex: " + searchQuery
    return re.compile(searchQuery, re.IGNORECASE)

  def setYMDregex(self):
    month_nums = ["01","02","03","04","05","06","07","08","09","10","11","12","1","2","3","4","5","6","7","8","9"]
    days = ["01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31","1","2","3","4","5","6","7","8","9"]
    years = ["2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020","2021","2022", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22"]

    reMonth = self.arrayToOr(month_nums)
    reDay = self.arrayToOr(days)
    reYear = self.arrayToOr(years)

    searchQuery = "\\b"+reYear+"[/-]"+reMonth+"[/-]"+reDay+"\\b"

    #print "YMD Regex: " + searchQuery
    return re.compile(searchQuery, re.IGNORECASE)


  def setMDregex(self):
    month_nums = ["01","02","03","04","05","06","07","08","09","10","11","12","1","2","3","4","5","6","7","8","9"]
    days = ["01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31","1","2","3","4","5","6","7","8","9"]
    years = ["2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020","2021","2022", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22"]

    reMonth = self.arrayToOr(month_nums)
    reDay = self.arrayToOr(days)
    reYear = self.arrayToOr(years)

    searchQuery = "\\b"+reMonth+"[/-]"+reDay+"\\b"

    #print "MD Regex: " + searchQuery
    return re.compile(searchQuery, re.IGNORECASE)


  def arrayToOr(self, sentArray):
    sentArray = [item.replace(' ', '[\\s\\r\\t\\n]*') for item in sentArray]
    joinStr = "|".join(sentArray)
    joinStr = "("+joinStr+")"
    return joinStr




  def writableLongJSON(self, sentString):
    sendString = sentString.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
    return sendString

  def readableLongJSON(self, sentString):
    sendString = sentString.replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t")
    return sendString


  def intConvert(self, s):
    sendNum = 0
    s = s.replace("\\n", " ").replace("\\t", " ").replace("\\r", " ")
    s = s.replace(" ", "")
    s = s.strip()
    try: 
        sendNum = int(s)
    except ValueError:
        sendNum = 0

    return sendNum

  def twodigitNum(self, dayNum):
    returnString = ""
    if dayNum>31 or dayNum == 0:
      returnString = ""
    elif dayNum<10:
      returnString = "0"+str(dayNum)
    else:
      returnString = str(dayNum)
    
    return returnString