# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

from feedgen.feed import FeedGenerator

class RssJobsFeedPipeline(object):
    def __init__(self, **kwargs):
        self.feeds = {} # Dictionary of per-spider feeds
        # Create unified feed
        self.fg = FeedGenerator()
        self.fg.title("Test RSS (all spiders)")
        self.fg.link(href='http://example.com')
        self.fg.description("Test RSS Jobs (unified)")
        dispatcher.connect(self.close_unified_feed, signals.engine_stopped)

    def _add_item_to_feed(self, fg, item):
        fe = fg.add_entry()
        fe.id(item['source'])
        fe.link({'href':item['source']})
        fe.title("[%(company)s] %(title)s @%(location)s" % item)
        fe.description( item['descText'] )

    def close_unified_feed(self):
        self.fg.rss_file('rss.xml')

    def open_spider(self, spider):
        self.feeds[spider] = fg = FeedGenerator()
        fg.title("Test RSS (Spider=%s)" % spider.name)
        fg.link(href='http://example.com')
        fg.description("Test RSS Jobs")

    def process_item(self, item, spider):
        self._add_item_to_feed(self.feeds[spider], item)
        self._add_item_to_feed(self.fg, item)
        return item

    def close_spider(self, spider):
        fg = self.feeds[spider]
        fg.rss_file('rss_%s.xml' % spider.name)
