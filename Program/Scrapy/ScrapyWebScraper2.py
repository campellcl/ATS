"""
TODO:
"""
import os
import collections
from Program.Scrapy.Items import HikerItem
from scrapy.spiders import Spider
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from scrapy import Request
from scrapy.selector import Selector


class HikerScraper(Spider):
    """
    HikerScraper(Spider)
    Scrapes information for a single hiker from both domains.
    """
    name = "hiker_scraper"
    allowed_domains = ['www.trailjournals.com', 'www.trailjournals.com/about.cfm?']
    start_urls = []

    """
    get_hiker_urls -Retrieves a list of all hiker urls to be scraped. The URL's retrieved are user_id's in the file
        "at-hikers.txt" who do not already appear in the storage directory as a .json file.
    @return hiker_urls -A list of hiker journal entry url's that have yet to be scraped.
    """
    def get_hiker_urls(self):
        hiker_urls = []
        start_url = "http://www.trailjournals.com/about.cfm?trailname="
        cwd = os.getcwd()
        read_location = "C:/Users/Chris/Documents/GitHub/ATS/Data/Hiker_Data"
        os.chdir(read_location)
        at_hikers = open("at-hikers.txt", 'r')
        storage_location = "C:/Users/Chris/Documents/GitHub/ATS/Data/Hiker_Data"
        for line in iter(at_hikers):
            line = line.strip('\n')
            hiker_fname = storage_location + "/" + line + ".json"
            if not os.path.isfile(hiker_fname):
                hiker_url = start_url + line
                hiker_urls.append(hiker_url)
        at_hikers.close()
        os.chdir(cwd)
        return hiker_urls

    """
    start_requests -Overridden method in charge of loading the hiker urls into the spider's start_urls parameter.
    @yield Request -A Scrapy Request object with a callback of parse_item.
    """
    def start_requests(self):
        for url in self.get_hiker_urls():
            yield Request(url, self.parse_hiker_info)

    """
    extract_hiker_id -Extracts the hiker's id from the about url returned by scrapy.
    @param response -The HtmlResponse object returned by scrapy.
    @return hiker_id -The unique identifier contained in the response URL.
    """
    def extract_hiker_id(self, response):
        hiker_url = response.url
        hiker_url_start = str.find(hiker_url, "trailname=", 0, len(hiker_url)) + len("trailname=")
        hiker_id = hiker_url[hiker_url_start:len(hiker_url)]
        return hiker_id

    """
    extract_first_journal_url -Retrieves the url of the first journal entry.
    @param journal_url -The pre-existing url that links to a random journal entry (usually the first).
    @param response -The Scrapy HtmlResponse object of the presumed first journal entry.
    @return first_entry_url -The URL of the first journal entry.
    """
    def extract_first_journal_url(self, journal_url, response):
        first_entry_url_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]/table//tr[1]"
        first_entry_url = Selector(response=response).xpath(first_entry_url_xpath + "//a[contains(text(), 'First')]")
        if first_entry_url:
            # Not on the first journal page. Record the first entry url.
            first_entry_url = first_entry_url.__getattribute__("href")
            pass
        # Already on the first journal page.
        return first_entry_url

    """
    parse_hiker_info -Parses the necessary hiker information (everything but the journal) and
        updates self.hiker accordingly.
    @param response -The HtmlResponse object returned by Scrapy.
    @yield Request -A scrapy.request object to be enqueued by the Response cycle with a callback of parse_hiker_journal.
    """
    def parse_hiker_info(self, response):
        # TODO: Somehow obtain the Hiker's direction 'dir'.
        # TODO: Somehow obtain the Hiker's trail start date 'start_date'
        # TODO: Somehow obtain the Hiker's trail estimated end date 'end_date'
        print("Response received: %s" % response)
        print("Parsing Hiker Info from response: %s" % response)
        hiker = HikerItem()
        hiker['id'] = self.extract_hiker_id(response=response)
        hiker_name_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]/table//tr[2]/td//font[2]"
        hiker_name = Selector(response=response).xpath(hiker_name_xpath).extract()[0]
        hiker_name_start = str.find(hiker_name, "-", 0, len(hiker_name))
        hiker_name_end = str.find(hiker_name, "<", hiker_name_start, len(hiker_name))
        hiker_name = hiker_name[hiker_name_start + 1:hiker_name_end]
        hiker_name = str.strip(hiker_name, " ")
        hiker['name'] = hiker_name
        hiker_trail_name_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]/table//tr[2]/td//font[1]/b"
        hiker_trail_name = Selector(response=response).xpath(hiker_trail_name_xpath).extract()[0]
        hiker_trail_name_start = str.find(hiker_trail_name, ">", 0, len(hiker_trail_name))
        hiker_trail_name_end = str.find(hiker_trail_name, "<", hiker_trail_name_start, len(hiker_trail_name))
        hiker_trail_name = hiker_trail_name[hiker_trail_name_start + 1:hiker_trail_name_end]
        hiker['trail_name'] = hiker_trail_name
        hiker['about_url'] = response.url
        # TODO: Verify that the 'journal_url' is the FIRST journal entry.
        hiker['journal_url'] = str.replace(response.url, "about", "entry")
        journal_parse_request = Request(hiker['journal_url'], callback=self.parse_hiker_journal)
        journal_parse_request.meta['hiker'] = hiker
        yield journal_parse_request
        # yield Request(hiker['journal_url'], callback=self.parse_hiker_journal)

    """
    journal_has_next_entry -Determines if the current journal entry has a following entry.
    @param response -A Scrapy HtmlResponse object of the journal entry in question.
    @return boolean -True if there is a following journal entry, False otherwise.
    """
    def journal_has_next_entry(self, response):
        next_entry_url_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]/table//tr[1]"
        next_entry_url = Selector(response=response).xpath(next_entry_url_xpath + "//a[contains(text(), 'Next')]")
        if next_entry_url:
            return True
        else:
            return False

    """
    extract_journal_entry_date -Uses Scrapy xpath Selectors to obtain the date of the current journal entry.
    @param response -The Scrapy HtmlResponse object containing the journal entry.
    @return entry_date -The date that the current journal entry was made, None if no date was provided.
    """
    def extract_entry_date(self, response):
        entry_date_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]/table//tr[2]/td/div/font/i"
        entry_date = Selector(response=response).xpath(entry_date_xpath).extract()[0]
        if entry_date:
            entry_date = str.replace(entry_date, "<i>", "")
            entry_date = str.replace(entry_date, "</i>", "")
            return entry_date
        else:
            return None

    """
    extract_next_entry_url -Uses Scrapy xpath Selectors to obtain the url for the next journal entry.
    @param response -The Scrapy HtmlResponse object containing the journal entry.
    @return next_entry_url -The url for the next journal entry if present, None otherwise.
    """
    def extract_next_entry_url(self, response):
        navbar_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]//table[1]//tr[1]//td[1]"
        next_entry_url = Selector(response=response).xpath(navbar_xpath + "//*[contains(text(), 'Next')]").extract()[0]
        if next_entry_url:
            next_entry_url = next_entry_url[str.find(next_entry_url, "id", 0, len(next_entry_url)):len(next_entry_url)]
            next_entry_url = next_entry_url[0:str.find(next_entry_url, ">")]
            next_entry_url = str.strip(next_entry_url, "\"")
            next_entry_url = "entry.cfm?" + next_entry_url
            next_entry_url = response.urljoin(next_entry_url)
            return next_entry_url
        else:
            return None

    """
    extract_prev_entry_url -Uses Scrapy xpath Selectors to obtain the url for the previous journal entry.
    @param response -The Scrapy HtmlResponse object containing the journal entry.
    @return next_entry_url -The url for the previous journal entry if present, None otherwise.
    """
    def extract_prev_entry_url(self, response):
        navbar_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]//table[1]//tr[1]//td[1]"
        prev_entry_url = Selector(response=response).xpath(navbar_xpath + "//a[contains(text(), 'Previous')]").extract()[0]
        if prev_entry_url:
            prev_entry_url = prev_entry_url[str.find(prev_entry_url, "id", 0, len(prev_entry_url)):len(prev_entry_url)]
            prev_entry_url = prev_entry_url[0:str.find(prev_entry_url, ">")]
            prev_entry_url = str.strip(prev_entry_url, "\"")
            prev_entry_url = "entry.cfm?" + prev_entry_url
            prev_entry_url = response.urljoin(prev_entry_url)
            return prev_entry_url
        else:
            return None

    """
    extract_entry_destination -Uses Scrapy xpath Selectors to obtain the destination listed in the journal entry.
    @param response -The Scrapy HtmlResponse object containing the journal entry.
    @return destination -The text entered in the journal for the destination if present, None otherwise.
    """
    def extract_entry_destination(self, response):
        trip_info_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]//table[1]//tr[3]"
        destination = Selector(response=response).xpath(trip_info_xpath + "//*[contains(text(), 'Destination')]")
        if destination:
            destination = destination.extract()
            return destination
        else:
            return None

    """
    """
    def extract_entry_start_loc(self, response):
        trip_info_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]//table[1]//tr[3]"
        start_loc = Selector(response=response).xpath(trip_info_xpath + "//*[contains(text(), 'Starting Location')]")
        if start_loc:
            start_loc = start_loc.extract()
            return start_loc
        else:
            return None

    def extract_entry_trip_mileage(self, response):
        trip_info_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]//table[1]//tr[3]"
        entry_trip_mileage = Selector(response=response).xpath(trip_info_xpath + "//*[contains(text(), 'Trip Miles')]")
        if entry_trip_mileage:
            entry_trip_mileage = float(entry_trip_mileage)
            return entry_trip_mileage
        else:
            return None

    def extract_entry_day_mileage(self, response):
        trip_info_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]//table[1]//tr[3]"
        day_mileage = Selector(response=response).xpath(trip_info_xpath + "//*[contains(text(), 'Today's Miles')]")
        if day_mileage:
            day_mileage = float(day_mileage)
            return day_mileage
        else:
            return None

    def parse_hiker_journal_entry(self, response):
        hiker = response.meta['hiker']
        hiker_journal = hiker['journal']
        entry = {}
        entry['date'] = self.extract_entry_date(response=response)
        entry['next_entry'] = self.extract_next_entry_url(response=response)
        entry['prev_entry'] = self.extract_prev_entry_url(response=response)
        entry['dest'] = self.extract_entry_destination(response=response)
        entry['start_loc'] = self.extract_entry_start_loc(response=response)
        entry['trip_mileage'] = self.extract_entry_trip_mileage(response=response)
        entry['day_mileage'] = self.extract_entry_day_mileage(response=response)
        journal_entry_num = len(hiker_journal)
        hiker_journal[journal_entry_num] = entry
        return hiker

    """
    parse_hiker_journal -Parses every journal entry by issuing a new scrapy.request HtmlRequest object
        for every consecutive journal entry.
    @param response -A Scrapy HtmlResponse object of the hiker's journal entry which is usually (but not guaranteed) to
        be the first journal entry.
    """
    def parse_hiker_journal(self, response):
        print("Response received: %s" % response)
        print("Parsing Hiker Journal from response: %s" % response)
        hiker = response.meta['hiker']
        hiker['journal_url'] = self.extract_first_journal_url(journal_url=hiker['journal_url'], response=response)
        hiker_journal = collections.OrderedDict()
        # Populate hiker_journal with first page's information.
        entry_num = 0
        entry = {}
        entry['date'] = self.extract_entry_date()
        entry['next_entry'] = self.extract_next_entry_url()
        entry['prev_entry'] = self.extract_prev_entry_url()
        entry['dest'] = self.extract_entry_destination()
        entry['start_loc'] = self.extract_entry_start_loc()
        entry['trip_mileage'] = self.extract_entry_trip_mileage()
        entry['day_mileage'] = self.extract_entry_day_mileage()
        hiker_journal[entry_num] = entry
        entry_num += 1
        if self.journal_has_next_entry(response=response):
            next_entry_parse_request = Request(url=entry['next_entry'], callback=self.parse_hiker_journal_entry)
            next_entry_parse_request.meta['hiker'] = hiker
            yield next_entry_parse_request
        else:
            yield hiker

def main():
    settings = get_project_settings()
    # TODO: Initialize item pipelines
    # settings.set('ITEM_PIPELINES', {'Program.Scrapy.Items.HikerJournalWriterPipeline': 2})
    crawler = CrawlerProcess(settings=settings)
    spider = HikerScraper()
    crawler.crawl(spider, domain="http://www.trailjournals.com")
    crawler.start()

if __name__ == '__main__':
    main()
