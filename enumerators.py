from enum import Enum

class SiteTypes(Enum):
  ListEvents = 1
  ListLinks = 2

class PaginationTypes(Enum):
  AllPages = 1
  NextPage = 2
  