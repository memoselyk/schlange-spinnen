from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

from jobs.items import JobsItem

import anydbm   # For dev only
import atexit

class OccMundialSpinne(CrawlSpider):
    name = 'occ'
    allowed_domains = ['occ.com.mx']
    start_urls = [
        "https://www.occ.com.mx/Buscar_Empleo/Resultados?"
        "bdtype=OCCM&q=python&hits=50&page=1&f=true",
    ]

    rules = (
        # TODO: Make this crawler check all result pages
        #Rule(
        #    SgmlLinkExtractor(allow=('Buscar_Empleo\/Resultados',)),
        #    callback='parse_page',follow=True),
        Rule(
            SgmlLinkExtractor(
                allow=('Empleo\/Oferta\/',)
            ),
            callback='parse_page_oferta',
            process_links='cleanup_oferta_url'),
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

    def cleanup_oferta_url(self, links):
        """All oferta links have a extra url params, that are not required.
        Get ride of them."""
        def __cleanup(link):
            if '?' in link.url:
                link.url = link.url.split('?')[0]
            return link
        return map(__cleanup, links)

    def parse_page_oferta(self, response):
        hxs = Selector(response)
        content_d = hxs.xpath( "//div[contains(@id,'content_d')]" )

        item = JobsItem()
        item['source']      = response.url
        item['title']       = content_d.xpath(
                './/div[@id="tittlejob_jo"]/h2/text()').extract()[0]
        #item['postDate']    = None
        #item['expireDate']  = None
        item['company']     = content_d.xpath(
                './/div[@id="tittlejob_jo"]/h3/text()').extract()[0].split(': ', 1)[1]
        # Most of items have the location in 'dl/dd[4]', but that is not guaranteed
        # to find the location correctly, look each term until the location is found
        location = ''
        for n, term in enumerate(content_d.xpath('.//div[@id="col1_jo"]//dl/dt')):
            def getText(tag):
                tag_texts = tag.xpath('text()').extract()
                return '' if len(tag_texts) == 0 else tag_texts[0]
            term_text = getText(term)
            if 'localidad' in term_text.lower():
                location = getText(content_d.xpath('.//div[@id="col1_jo"]//dl/dd[%d]' % (n+1)))
                break
        item['location'] = 'N/A' if location == '' else location
        desc = content_d.xpath('//div[@class="txt2_jo"]')
        #item['descText'] = '\n'.join(desc.xpath( 'pre//text()' ).extract())
        # TODO: Have a better "html->text" converter, to handle <i>C</i><i>ases</i> like this
        item['descText'] = '\n'.join(
                # remove blank lines...
                filter(lambda s:s.strip(),
                # ... from all innerText
                desc.xpath( './/text()' ).extract()))

        item['descHtml'] = ''.join(
                # remove the "enviar mi curriculum" buttons...
                filter(lambda s:'<input' not in s,
                # remove blank lines ...
                filter(lambda s:len(s.strip())!=0,
                # ... from the innerHtml
                desc.xpath( 'node()' ).extract())))
        return item
