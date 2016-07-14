"""
ScrapyWebScraper.py
Scrapes the Appalachian trail journal website for relevant information using the Scrapy module.
 @Author: Chris Campell
 @Version: 7/5/2016
"""

import sys
import os
import json
import scrapy
from scrapy import signals
from twisted.internet import reactor
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from scrapy.spiders import BaseSpider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.crawler import Crawler, CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.linkextractors import LinkExtractor
from scrapy.item import Item
from scrapy import Request
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor

"""
HikerItem(Item) -A scrapy.Item that functions as a dictionary and houses information retrieved by the web scrapers.
@Author: Chris Campell
@Version: 7/14/2016
"""
class HikerItem(Item):
    name = scrapy.Field()
    trail_name  = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    about_url = scrapy.Field()
    journal_url = scrapy.Field()
    dir = scrapy.Field()

"""
HikerInfoScraper(BaseSpider) -A scrapy.spiders.BaseSpider web spider which obtains hiker information.
@Author: Chris Campell
@Version: 7/14/2016
"""
class HikerInfoScraper(BaseSpider):
    name = "hiker_info_base_spider"
    allowed_domains = ['www.trailjournals.com', 'www.trailjournals.com/about.cfm?']

    '''
    def __init__(self, *args, **kwargs):
        print(__name__)
        if __name__ == '__main__':
            start_urls = kwargs.get('start_url')
            self.start_urls = start_urls
            super(HikerInfoScraper, self).__init__(*args, start_urls)
    '''


    """
    parse -A method that is part of the Scrapy Response Architecture Cycle (RAC), which
     yields all retrieved hiker information.
     @param response -The response object returned by the RAC.
     @yield hiker -A sub-classed scrapy.Item which functions as a dictionary and houses hiker information.
    """
    def parse(self, response):
        print("Response received: %s" % response)
        print("Parsing Hiker info from response: %s" % response)
        hiker = HikerItem()
        hiker_trail_name_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]/table//tr[2]/td//font[1]/b"
        hiker_trail_name = Selector(response=response).xpath(hiker_trail_name_xpath).extract()[0]
        hiker_trail_name_start = str.find(hiker_trail_name, ">", 0, len(hiker_trail_name))
        hiker_trail_name_end = str.find(hiker_trail_name, "<", hiker_trail_name_start, len(hiker_trail_name))
        hiker_trail_name = hiker_trail_name[hiker_trail_name_start + 1:hiker_trail_name_end]
        hiker['trail_name'] = hiker_trail_name
        hiker['about_url'] = response.url
        hiker_name_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]/table//tr[2]/td//font[2]"
        hiker_name = Selector(response=response).xpath(hiker_name_xpath).extract()[0]
        hiker_name_start = str.find(hiker_name, "-", 0, len(hiker_name))
        hiker_name_end = str.find(hiker_name, "<", hiker_name_start, len(hiker_name))
        hiker_name = hiker_name[hiker_name_start + 2:hiker_name_end]
        hiker['name'] = hiker_name
        hiker['journal_url'] = str.replace(hiker['about_url'], "about", "entry")
        yield hiker


class HikerInfoWriterPipeline(object):
    def __init__(self):
        self.file = open('hiker-info.json', 'w')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

class ScrapyWebScraper(CrawlSpider):
    name = "trailjournal"
    allowed_domains = ['www.trailjournals.com', 'www.trailjournals.com/about.cfm?', 'www.trailjournals.com/entry.cfm?']
    start_urls = ["http://www.trailjournals.com/about.cfm?trailname=860"]

    rules = (
        # Rule(LinkExtractor(allow='http://www.trailjournals.com/about.cfm?trailname=860'), callback='parse_item'),
        # Rule(LinkExtractor(allow='www.trailjournals.com/about.cfm"trailname=860'), follow=True, callback='parse_item'),
        Rule(LinkExtractor(), callback='parse_item'),
        # Rule(SgmlLinkExtractor(allow='http://www.trailjournals.com/about.cfm?trailname=860'), callback='parse_item')
    )

    """
    parse_start_url -Overridden method that handles the parser's start_url callback.
    @Override: crawl.py
    @param response -The response object returned by the spider.
    """
    def parse_items(self, response):
        # Parsing Hiker Info..
        hiker = self.parse_hiker_info(response)

    """
    parse_links -Helper method for the callback of the start_url.
    @param response -The response object returned by the spider.
    """
    def parse_links(self, response):
        print("PARSE LINKS: Parsing response from %s" % response.url)
        hiker_name_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table/tbody/tr[2]/td/font[2]"
        hiker_trail_name_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table/tbody/tr[2]/td/font[1]"
        hiker_info_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table/tbody"
        # about_url_xpath = sidebar_xpath + "//tr//td//*[contains(text(), 'About')]/.."
        hiker = HikerItem()
        about_url_xpath = "/html/body/table//tr[4]/td/table/tr/td//table[3]//tr[4]/td/a"
        about_url = Selector(response=response).xpath(about_url_xpath).extract()[0]
        about_url_start = str.find(about_url, "\"", 0, len(about_url))
        about_url_end = str.find(about_url, "\"", about_url_start + 1, len(about_url))
        about_url = about_url[about_url_start + 1:about_url_end]
        about_url = response.urljoin(about_url)
        hiker['about_url'] = about_url
        yield hiker

    '''
    def parse_hiker_info(self, response):
        print("Response received: %s" % response)
        print("Parsing Hiker info from response: %s" % response)
        hiker = HikerItem()
        hiker_trail_name_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]/table//tr[2]/td//font[1]/b"
        hiker_trail_name = Selector(response=response).xpath(hiker_trail_name_xpath).extract()[0]
        hiker_trail_name_start = str.find(hiker_trail_name, ">", 0, len(hiker_trail_name))
        hiker_trail_name_end = str.find(hiker_trail_name, "<", hiker_trail_name_start, len(hiker_trail_name))
        hiker_trail_name = hiker_trail_name[hiker_trail_name_start + 1:hiker_trail_name_end]
        hiker['trail_name'] = hiker_trail_name
        hiker['about_url'] = response.url
        hiker_name_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]/table//tr[2]/td//font[2]"
        hiker_name = Selector(response=response).xpath(hiker_name_xpath).extract()[0]
        hiker_name_start = str.find(hiker_name, "-", 0, len(hiker_name))
        hiker_name_end = str.find(hiker_name, "<", hiker_name_start, len(hiker_name))
        hiker_name = hiker_name[hiker_name_start + 2:hiker_name_end]
        hiker['name'] = hiker_name
        hiker['journal_url'] = str.replace(hiker['about_url'], "about", "entry")
        print("Preliminary Hiker Info Recorded.")
        print("Requesting External (Allowed) Response: %s" % hiker['journal_url'])
        return hiker
    '''

    def parse_hiker_journal(self, response, hiker):
        print("Parsing Hiker Journal...")

"""
"""
def get_hiker_urls():
    hiker_urls = []
    start_url = "http://www.trailjournals.com/entry.cfm?trailname="
    at_hikers = open("at-hikers.txt", 'r')
    storage_location = "C:/Users/Chris/Documents/GitHub/ATS/Data/Hiker_Data"
    for line in iter(at_hikers):
        line = line.strip('\n')
        hiker_fname = storage_location + "/" + line + ".json"
        if not os.path.isfile(hiker_fname):
            hiker_url = start_url + line
            hiker_urls.append(hiker_url)
    at_hikers.close()
    return hiker_urls

def main(cmd_args):
    settings = get_project_settings()
    settings.set('ITEM_PIPELINES', {'__main__.HikerInfoWriterPipeline': 0})
    crawler = CrawlerProcess(settings=settings)
    # crawler = CrawlerProcess(get_project_settings())
    hiker_urls = get_hiker_urls()
    spider = HikerInfoScraper()
    crawler.crawl(spider, start_url=hiker_urls)
    crawler.start()
    # process.crawl(HikerInfoScraper(start_url=hiker_urls), domain="http://www.trailjournals.com")
    '''
    process.crawl(ScrapyWebScraper, domain="http://www.trailjournals.com")
    process.start()
    '''

if __name__ == '__main__':
    main(sys.argv)
