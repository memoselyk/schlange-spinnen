# Scrapy settings for jobs project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'jobs'

SPIDER_MODULES = ['jobs.spiders']
NEWSPIDER_MODULE = 'jobs.spiders'

DOWNLOADER_MIDDLEWARES = {
    # Use enabled downloader, if required
    'jobs.middleware.SeleniumDriverDownloader': 990,
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'jobs (+http://www.yourdomain.com)'
USER_AGENT = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/31.0.1650.63 Chrome/31.0.1650.63 Safari/537.36'
