"""
ScrapyWebScraper.py
Scrapes the Appalachian trail journal website for relevant information using the Scrapy package.
 @Author: Chris Campell
 @Version: 7/5/2016
"""

import os
import sys
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class ScrapyWebScraper(CrawlSpider):
    name = "trailjournal"
    allowed_domains = ['http://www.trailjournals.com']
    start_urls = ["http://www.trailjournals.com/entry.cfm?trailname=859", "http://www.trailjournals.com/entry.cfm?trailname=860"]

    rules = (
        Rule(LinkExtractor(allow='http://www.trailjournals.com/about.cfm?trailname=859'), callback='parse_item'),
        Rule(LinkExtractor(allow='http://www.trailjournals.com/about.cfm?trailname=860'), callback='parse_item')
    )

    def parse_item(self, response):
        print("This is an item page!")
        self.logger.info('Hi, this is an item page! %s' % response.url)
        '''
        start_url = "http://www.trailjournals.com/entry.cfm?trailname="
        at_hikers = open("at-hikers.txt", 'r')
        storage_location = "C:/Users/Chris/Documents/GitHub/ATS/Data/Hiker_Data"
        for line in iter(at_hikers):
            hiker_fname = storage_location + "/" + str.strip(line, '\n') + ".json"
            if not os.path.isfile(hiker_fname):
                hiker_url = start_url + line
                hiker_url_response = HtmlResponse(url=hiker_url)
                sidebar_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[1]/table[1]/tbody/tr/td/table[3]"
                homepage_selector = Selector(response=hiker_url_response).xpath(query="/html/body")
                sidebar_selector = Selector(response=hiker_url_response).xpath(query=sidebar_xpath)
                about_url_xpath = sidebar_xpath + "//tr//td//*[contains(text(), 'About')]/.."
                hiker_about_button = Selector(response=hiker_url_response).xpath(about_url_xpath)
                print(hiker_url_response.text)
            else:
                print("Hiker id: %d has already been logged." % int(line))
        at_hikers.close()
        '''

def main(cmd_args):
    process = CrawlerProcess(get_project_settings())
    # Start the trailjournal scraper.
    process.crawl(ScrapyWebScraper, domain="http://www.trailjournals.com")
    process.start()

if __name__ == '__main__':
    main(sys.argv)


