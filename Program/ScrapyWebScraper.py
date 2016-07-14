"""
ScrapyWebScraper.py
Scrapes the Appalachian trail journal website for relevant information using the Scrapy package.
 @Author: Chris Campell
 @Version: 7/5/2016
"""

import sys
import scrapy
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.linkextractors import LinkExtractor
from scrapy.item import Item
from scrapy import Request
# from scrapy.linkextractors.sgml import SgmlLinkExtractor

class HikerItem(Item):
    name = scrapy.Field()
    trail_name  = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    about_url = scrapy.Field()
    journal_url = scrapy.Field()
    dir = scrapy.Field()


class ScrapyWebScraper(CrawlSpider):
    name = "trailjournal"
    allowed_domains = ['www.trailjournals.com', 'www.trailjournals.com/about.cfm?', 'www.trailjournals.com/entry.cfm?']
    start_urls = ["http://www.trailjournals.com/about.cfm?trailname=860"]
    '''
    rules = (
        # Rule(LinkExtractor(allow='http://www.trailjournals.com/about.cfm?trailname=860'), callback='parse_item'),
        # Rule(LinkExtractor(allow='www.trailjournals.com/about.cfm"trailname=860'), follow=True, callback='parse_item'),
        Rule(LinkExtractor(), callback='parse_item'),
        # Rule(SgmlLinkExtractor(allow='http://www.trailjournals.com/about.cfm?trailname=860'), callback='parse_item')
    )
    '''

    """
    parse_start_url -Overridden method that handles the parser's start_url callback.
    @Override: crawl.py
    @param response -The response object returned by the spider.
    """
    def parse_start_url(self, response):
        self.parse_hiker_info(response)

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
        # yield Request(scrapy_about_url, callback=self.parse_hiker_info)
        # sidebar = Selector(response=response).xpath(sidebar_xpath).extract()
        home = Selector(response=response).xpath("/html/body/table")
        about_url = Selector(response=response).xpath("/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[1]/table[1]/tbody/tr/td/table[3]/tbody").extract()
        about_url_two = Selector(response=response).xpath("/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[1]/table[1]/tbody/tr/td/table[3]/tbody/tr[4]/td").extract()
        Selector(response=response).xpath('//a').extract()
        '''

    def parse_hiker_info(self, response):
        print("Response received: %s" % response)
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
        print("Requesting External (Allowed) Response: %s." % hiker['journal_url'])
        # yield Request(hiker['journal_url'], callback='parse_hiker_journal')

    def parse_hiker_journal(self, response):
        print("Callback Received: Executing...")

    """
    parse_item -
    """
    def parse_item(self, response):
        hiker_name_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table/tbody/tr[2]/td/font[2]"
        hiker_trail_name_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table/tbody/tr[2]/td/font[1]"
        hiker_info_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table/tbody"
        print("This is an item page!")
        self.logger.info('Hi, this is an item page! %s' % response.url)
        hxs = HtmlXPathSelector(response)
        item = Item()
        item['name'] = hxs.select(hiker_name_xpath).extract()
        return item

def main(cmd_args):
    process = CrawlerProcess(get_project_settings())
    # Start the trailjournal scraper.
    process.crawl(ScrapyWebScraper, domain="http://www.trailjournals.com")
    process.start()

if __name__ == '__main__':
    main(sys.argv)
