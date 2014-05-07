from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

from jobs.items import JobsItem

import anydbm   # For dev only
import atexit

class ComputrabajoSpinne(CrawlSpider):
    name = 'computrabajo'
    allowed_domains = ['computrabajo.com.mx']
    start_urls = [
        "http://www.computrabajo.com.mx/bt-ofrlistado.htm?BqdPalabras=python"
    ]

    rules = (
        # TODO: Make this crawler check all result pages
        #Rule(
        #    SgmlLinkExtractor(allow=('Buscar_Empleo\/Resultados',)),
        #    callback='parse_page',follow=True),
        Rule(
            SgmlLinkExtractor(allow=('bt-ofrd-',)),
            callback='parse_offer_page',
            process_links='cleanup_offer_url'),
    )

    def __init__(self, **kwargs):
        CrawlSpider.__init__(self)
        if 'usedb' in kwargs:
            # Connect signals for dbfile
            dispatcher.connect(self.open_dbfile, signals.spider_opened)
            dispatcher.connect(self.item_dbfile, signals.item_scraped)
            dispatcher.connect(self.close_dbfile, signals.spider_closed)

    def open_dbfile(self, spider):
        if spider is not self : return
        self.db = anydbm.open(".cache.%s.db" % self.name, 'c')

    def item_dbfile(self, spider, item, response):
        if spider is not self : return
        self.db[response.url] = response.body

    def close_dbfile(self, spider):
        if spider is not self : return
        self.db.close()

    def cleanup_offer_url(self, links):
        """All offer links have a extra url params, that are not required.
        Get rid of them."""
        def __cleanup(link):
            if '?' in link.url:
                link.url = link.url.split('?')[0]
            return link
        return map(__cleanup, links)

    def parse_offer_page(self, response):
        hxs = Selector(response)
        offer_content = hxs.xpath("/html/body/center/table/tr[4]/td[3]/table/tr/td/table")[0]
        def extract_row_by_title(title):
            return offer_content.xpath(".//tr[td//text()='%s']" % title).xpath(
                    ".//td[2]//text()").extract()[0]

        item = JobsItem()
        item['source'] = response.url
        item['title'] = offer_content.xpath('.//tr[4]//text()').extract()[0]
        #item['postDate'] = None
        #item['expireDate'] = None
        item['company'] = extract_row_by_title('Empresa:')
        item['location'] = '%s, %s' % (extract_row_by_title('Localidad:'), extract_row_by_title('Estado:'))

        desc = offer_content.xpath("./tr[6]")
        # TODO: Have a better "html->text" converter, to handle <i>C</i><i>ases</i> like this
        item['descText'] = '\n'.join(
                # remove blank chars...
                map(lambda s:s.strip(),
                # ... from all innerText
                desc.xpath( './/text()' ).extract()))

        item['descHtml'] = ''.join(
                # remove blank lines ...
                filter(lambda s:len(s.strip())!=0,
                # ... from the innerHtml
                desc.xpath( 'node()' ).extract()))
        return item
