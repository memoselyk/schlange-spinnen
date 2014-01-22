# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class JobsItem(Item):
    source      = Field()   # Page (url) where it was found
    title       = Field()   # Title of posting
    # Following items are TBD
    #postDate    = Field()
    #expireDate  = Field()
    company     = Field()   # Offering company
    location    = Field()   # Work location (if available)
    descText    = Field()   # Text of the job
    descHtml    = Field()
    # From the description could later extract:
    # languages, tools, methodologies, ...
