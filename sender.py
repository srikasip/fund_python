import requests
import json

def main():
  # localhost:3000
  url = 'http://fundue.herokuapp.com/events/processedJsonListener'
  headers = {'Accept' : 'application/json', 'Content-Type' : 'application/json; charset=UTF-8', "pageEncoding":"UTF-8"}
  r = requests.post(url, data=open('EventsOutput/allProcessedData.json', 'rb'), headers=headers)
  obj = r.json()
  print "successfully saved " + obj["saved"] + " of " + obj["total"]

if __name__ == "__main__": main()