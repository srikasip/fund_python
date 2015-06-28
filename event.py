#!/usr/bin/python3
#this is the class for 1 single event

class Event:
  def __init__(self):
    self.source = ""
    self.name = ""
    self.location = ""
    self.description = ""
    self.datetime = ""
    self.price = ""
    self.imagePath = ""
    self.dump = ""

  def cleanContent(self):
    self.source = self.returnString(self.source)
    self.name = self.returnString(self.name)
    self.location = self.returnString(self.location)
    self.description = self.returnString(self.description)
    self.datetime = self.returnString(self.datetime)
    self.price = self.returnString(self.price)
    self.imagePath = self.returnString(self.imagePath)
    self.dump = self.returnString(self.dump)

  def writeHTML(self):
    pass

  def writeJSON(self):
    jsonString = "{"
    jsonString += '"source":"' + str(self.source.replace('"',"'").replace("\n"," ").replace("\r"," ").replace("\t", " ")) + '",'
    jsonString += '"name":"' + str(self.name.replace('"',"'").replace("\n"," ").replace("\r"," ").replace("\t", " ")) + '",'
    jsonString += '"location":"' + str(self.location.replace('"',"'").replace("\n"," ").replace("\r"," ").replace("\t", " ")) + '",'
    jsonString += '"description":"' + str(self.description.replace('"',"'").replace("\n"," ").replace("\r"," ").replace("\t", " ")) + '",'
    jsonString += '"datetime":"' + str(self.datetime.replace('"',"'").replace("\n"," ").replace("\r"," ").replace("\t", " ")) + '",'
    jsonString += '"price":"' + str(self.price.replace('"',"'").replace("\n"," ").replace("\r"," ").replace("\t", " ")) + '",'
    jsonString += '"imagePath":"' + str(self.imagePath.replace('"',"'").replace("\n"," ").replace("\r"," ").replace("\t", " ")) + '",'
    jsonString += '"dump":"'+ self.dump.replace('"',"'").replace("\n","\\n").replace("\r","\\r").replace("\t", " ") + '"'
    jsonString += "}"
    return jsonString

  def returnString(self, sentArray):
    sendable = ""
    if((type(sentArray) is not None) and (sentArray != "")):
      return sentArray.strip()
    else:
      return sentArray

  def forceStr(self):
    self.name = self.nullOrString(self.name)
    self.location = self.nullOrString(self.location)
    self.description = self.nullOrString(self.description)
    self.datetime = self.nullOrString(self.datetime)
    self.price = self.nullOrString(self.price)
    self.imagePath = self.nullOrString(self.imagePath)
    self.dump = self.nullOrString(self.dump)

  def nullOrString(self, sent_string):
    if sent_string is None:
      return ""
    else:
      return sent_string.encode("utf-8").strip()

# self.name
# self.location
# self.description
# self.datetime
# self.price
# self.imagePath
# self.dump