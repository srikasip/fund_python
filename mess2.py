import requests
import json

def main():
  url = 'http://fundue.herokuapp.com/eventaggs/sendParserData'
  headers = {'Accept' : 'application/json', 'Content-Type' : 'application/json; charset=UTF-8', "pageEncoding":"UTF-8"}
  r = requests.post(url, data=open('parsingXPaths.json', 'rb'), headers=headers)
  obj = r.json()
  print "successfully saved " + obj["saved"] + " of " + obj["total"]

if __name__ == "__main__": main()