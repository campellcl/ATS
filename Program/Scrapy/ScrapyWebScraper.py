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
import lxml.etree as etree
from scrapy import signals
from twisted.internet import reactor
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from scrapy.spiders import Spider
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
    id = scrapy.Field()
    name = scrapy.Field()
    trail_name  = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    about_url = scrapy.Field()
    journal_url = scrapy.Field()
    dir = scrapy.Field()
    journal = scrapy.Field()

"""
HikerInfoScraper(BaseSpider) -A Scrapy Spider which obtains and records hiker information.
@Author: Chris Campell
@Version: 7/14/2016
"""
class HikerInfoScraper(Spider):
    name = "hiker_info_base_spider"
    allowed_domains = ['www.trailjournals.com', 'www.trailjournals.com/about.cfm?']
    start_urls = ["http://www.trailjournals.com/about.cfm?trailname=860"]

    """
    get_hiker_urls -Retrieves a list of all hiker urls to be scraped. The URL's retrieved are user_id's in the file
        "at-hikers.txt" who do not already appear in the storage directory as a .json file.
    @return hiker_urls -A list of hiker journal entry url's that have yet to be scraped.
    """
    def get_hiker_urls(self):
        hiker_urls = []
        start_url = "http://www.trailjournals.com/about.cfm?trailname="
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

    """
    start_requests -Overridden method in charge of loading the hiker urls into the spider's start_urls parameter.
    @yield Request -A Scrapy Request object with a callback of parse_item.
    """
    def start_requests(self):
        for url in self.get_hiker_urls():
            yield Request(url, self.parse)

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
        hiker_name = hiker_name[hiker_name_start + 1:hiker_name_end]
        hiker_name = str.strip(hiker_name, " ")
        hiker['name'] = hiker_name
        hiker['journal_url'] = str.replace(hiker['about_url'], "about", "entry")
        yield hiker

    '''
    def __init__(self, *args, **kwargs):
        print(__name__)
        if __name__ == '__main__':
            start_urls = kwargs.get('start_url')
            self.start_urls = start_urls
            super(HikerInfoScraper, self).__init__(*args, start_urls)
    '''
"""
HikerInfoWriterPipeline -A Scrapy Item Pipeline which writes HikerInfoScraper yielded items to output file:
    hiker-info.json
@Author: Chris Campell
@Version: 7/15/2016
"""
class HikerInfoWriterPipeline(object):
    """
    __init__ -Constructor for objects of type HikerInfoWriterPipeline; opens the output file for writing.
    """
    def __init__(self):
        self.file = open('hiker-info.json', 'w')

    """
    process_item -Writes each Spider yielded item to the output file: 'self.file'
    @return item -The item written to the output file.
    """
    def process_item(self, item, spider):
        # TODO: create a list of dictionaries and then use:
        # with open(file.json, 'w') as fp:
        # json.dump(obj, fp)
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
        print("parsing hiker info")
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

    def parse_hiker_journal(self, response, hiker):
        print("Parsing Hiker Journal...")

"""
HikerJournalWriterPipeline -A Scrapy Item Pipeline which writes HikerJournalScraper yielded items to output file:
    hiker-journals.json
@Author: Chris Campell
@Version: 7/15/2016
"""
class HikerJournalWriterPipeline(object):
    """
    __init__ -Constructor for objects of type HikerInfoWriterPipeline; opens the output file for writing.
    """
    def __init__(self):
        self.file = open('hiker-journals.json', 'w')

    """
    process_item -Writes each Spider yielded item to the output file: 'self.file'
    @return item -The item written to the output file.
    """
    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

"""
HikerJournalScraper -A Scrapy CrawlSpider which scrapes and stores hiker trail journal information.
@Author: Chris Campell
@Version: 7/15/2016
"""
class HikerJournalScraper(CrawlSpider):
    name = "hiker_journal_scraper"
    allowed_domains = ['www.trailjournals.com', 'www.trailjournals.com/about.cfm?', 'www.trailjournals.com/entry.cfm?']
    start_urls = ["http://www.trailjournals.com/about.cfm?trailname=860"]

    """
    get_hiker_urls -Retrieves a list of all hiker urls to be scraped. The URL's retrieved are user_id's in the file
        "at-hikers.txt" who do not already appear in the storage directory as a .json file.
    @return hiker_urls -A list of hiker journal entry url's that have yet to be scraped.
    """
    def get_hiker_urls(self):
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

    """
    start_requests -Overridden method in charge of loading the hiker urls into the spider's start_urls parameter.
    @yield Request -A Scrapy Request object with a callback of parse_item.
    """
    def start_requests(self):
        for url in self.get_hiker_urls():
            yield Request(url, self.parse_item)

    """
    entry_has_trip_info -Returns whether or not the current journal entry has a <td> with destination, trip-mileage,
        start_location, etc.
    @param response -The HtmlResponse object retrieved by Scrapy.
    @return boolean -True if the current journal entry has a <td> with destination, trip-mileage, start_location, etc;
        false otherwise.
    """
    def entry_has_trip_info(self, response):
        trip_info_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]//table[1]//tr[3]"
        info_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]/table//tr"
        #TODO: Try just using /*[contains(text(), '')] for Destination and Trip Mileage, etc..
        trip_info = Selector(response=response).xpath(info_xpath + "//*[contains(text(), 'Destination')]").extract()
        if trip_info:
            # Entry has trip information.
            return True
        else:
            return False

    """
    extract_entry_trip_info -Uses Scrapy xpath Selectors to obtain trip information from the current journal.
    @param response -The HtmlResponse object retrieved by Scrapy.
    @return entry_trip_info -A dictionary designed for data visualization containing the trip
        information (if any). If no trip info is available then a dictionary is returned containing trip information
        Key's with the Value set to "None".
    """
    def extract_entry_trip_info(self, response):
        trip_info = {}
        trip_info_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]//table[1]//tr[3]"
        trip_info = Selector(response=response).xpath(trip_info_xpath).extract()
        destination = Selector(response=response).xpath(trip_info_xpath + "//*[contains(text(), 'Destination')]")
        start_loc = Selector(response=response).xpath(trip_info_xpath + "//*[contains(text(), 'Starting Location']")
        day_mileage = Selector(response=response).xpath(trip_info_xpath + "//*[contains(text(), 'Today's Miles')]")
        trip_mileage = Selector(response=response).xpath(trip_info_xpath + "//*[contains(text(), 'Trip Miles')]")
        date = self.extract_journal_entry_date(response=response)
        if trip_mileage:
            trip_info['trip_mileage'] = int(trip_mileage)
        else:
            trip_info['trip_mileage'] = "None"
        if start_loc:
            trip_info['start_loc'] = start_loc
        else:
            trip_info['start_loc'] = "None"
        if day_mileage:
            trip_info['day_mileage'] = int(day_mileage)
        else:
            trip_info['day_mileage'] = "None"
        if date:
            trip_info['date'] = date
        else:
            trip_info['date'] = "None"
        if destination:
            trip_info['dest'] = destination
        else:
            trip_info['dest'] = "None"
        return trip_info

    """
    extract_next_journal_entry_url -Uses Scrapy xpath Selectors to obtain the url of the next journal entry.
    @param response -The HtmlResponse object retrieved by Scrapy.
    @return next_entry_url -The url of the next consecutive journal entry.
    """
    def extract_next_journal_entry_url(self, response):
        navbar_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]//table[1]//tr[1]//td[1]"
        next_entry_url = Selector(response=response).xpath(navbar_xpath + "//*[contains(text(), 'Next')]").extract()[0]
        next_entry_url = next_entry_url[str.find(next_entry_url, "id", 0, len(next_entry_url)):len(next_entry_url)]
        next_entry_url = next_entry_url[0:str.find(next_entry_url, ">")]
        next_entry_url = str.strip(next_entry_url, "\"")
        next_entry_url = "entry.cfm?" + next_entry_url
        next_entry_url = response.urljoin(next_entry_url)
        return next_entry_url

    """
    extract_journal_entry_date -Uses Scrapy xpath Selectors to obtain the date of the current journal entry.
    @param response -The HtmlResponse object retrieved by Scrapy.
    @return entry_date -The date that the current journal entry was made.
    """
    def extract_journal_entry_date(self, response):
        entry_date_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]/table//tr[2]/td/div/font/i"
        entry_date = Selector(response=response).xpath(entry_date_xpath).extract()[0]
        entry_date = str.replace(entry_date, "<i>", "")
        entry_date = str.replace(entry_date, "</i>", "")
        return entry_date

    """
    extract_journal_entry_text -Uses Scrapy xpath Selectors to obtain the text of the current journal entry.
    @param response -The HtmlResponse object retrieved by Scrapy.
    @return journal_entry -The text comprising the current journal entry.
    """
    def extract_journal_entry_text(self, response):
        journal_entry_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]/table[1]//tr[5]/td/blockquote/text()"
        journal_entry = Selector(response=response).xpath(journal_entry_xpath).extract()[1]
        journal_entry = str.replace(journal_entry, "\n", "")
        journal_entry = str.replace(journal_entry, "\t", "")
        journal_entry = str.replace(journal_entry, "\r", "")
        return journal_entry

    """
    extract_hiker_id -Extracts the hiker id from the Scrapy HtmlResponse url.
    @param response -The HtmlResponse object retrieved by Scrapy.
    @return hiker_id -The id extracted from the response url.
    """
    def extract_hiker_id(self, response):
        hiker_url = response.url
        hiker_url_start = str.find(hiker_url, "trailname=", 0, len(hiker_url)) + len("trailname=")
        hiker_id = hiker_url[hiker_url_start:len(hiker_url)]
        return hiker_id

    def parse_hiker_journal(self, response, hiker_item):
        journal_entry_num = 0
        hiker_journal = {}
        while journal_has_next_entry(response):
            hiker_journal_entry = self.extract_entry_trip_info(response=response)
            hiker_journal_entry['entry_num'] = journal_entry_num
            hiker_journal_entry['entry'] = self.extract_journal_entry_text(response=response)
            hiker_journal_entry['next_entry'] = self.extract_next_journal_entry_url(response=response)
            # Go to next journal entry.
            # yield Request(url=hiker_journal_entry['next_entry'], callback=self.parse_hiker_journal())
        return hiker_journal

    """
    parse_item -
    """
    def parse_item(self, response):
        hiker = HikerItem()
        hiker_journal = {}
        print("Response received: %s" % response)
        hiker['id'] = self.extract_hiker_id(response=response)
        print("Parsing Hiker Journal from response: %s" % response)
        navbar_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]//table[1]//tr[1]//td[1]"
        first_entry_url = Selector(response=response).xpath(navbar_xpath + "//*[contains(text(), 'First')]").extract()
        if not first_entry_url:
            # first_entry_url = []; already on the first journal page.
            hiker['journal_url'] = first_entry_url
            journal_entry_num = 0
        else:
            # Go to the first journal page.
            yield Request(url=first_entry_url, callback=self.parse_item)
        # Extract and store journal entry information
        yield Request(url=first_entry_url, callback=self.parse_hiker_journal(response=response))

def main(cmd_args):
    settings = get_project_settings()
    '''
    settings.set('ITEM_PIPELINES', {'__main__.HikerInfoWriterPipeline': 1})
    crawler = CrawlerProcess(settings=settings)
    spider = HikerInfoScraper()
    crawler.crawl(spider, domain="http://www.trailjournals.com")
    crawler.start()
    '''
    settings.set('ITEM_PIPELINES', {'__main__.HikerJournalWriterPipeline': 2})
    crawler = CrawlerProcess(settings=settings)
    spider = HikerJournalScraper()
    crawler.crawl(spider, domain="http://www.trailjournals.com")
    crawler.start()

if __name__ == '__main__':
    main(sys.argv)
