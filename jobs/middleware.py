from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy import log

import re

from selenium import webdriver
import atexit

class SeleniumDriverDownloader( object ):
    def __init__(self, userAgent=None):
        log.msg(format="SeleniumDownloader: Using user agent %(agent)r",
                level=log.DEBUG, agent=userAgent)
        caps = {}
        if userAgent is not None:
            caps['phantomjs.page.settings.userAgent'] = userAgent
        self.driver = webdriver.PhantomJS(desired_capabilities=caps)
        # Use cleanup to prevent a dangling browser process
        def _atexit_cleanup():
            log.msg("SeleniumDownloader: _atexit_cleanup", level=log.INFO)
            if self is not None :
                SeleniumDriverDownloader.__del__(self)
        atexit.register(_atexit_cleanup)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings['USER_AGENT'])

    def __del__(self):
        log.msg("SeleniumDownloader: Bye!", level=log.INFO)
        self.driver.quit()

    def process_request( self, request, spider ):

        # Test to disable this for other urls
        if not re.search('Buscar_Empleo\/Resultados', request.url):
            return

        log.msg(format="SeleniumDownloader: Processing request: %(request)r",
                level=log.INFO, request=request)
        if( type(request) is not FormRequest ):
            self.driver.get( request.url )
            renderedBody = self.driver.page_source
            return HtmlResponse( request.url, body=renderedBody, encoding='utf8' )
