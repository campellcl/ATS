"""
WebScraper.py
Uses urllib in conjunction with Scrapy to parse hiker information.
@Author: Chris Campell
@Version: 7/20/2016
"""

import os
import collections
from scrapy import Selector
from urllib.request import urlopen
import json
import time
import contextlib

"""
get_hiker_urls -Retrieves a list of all hiker urls to be scraped. The URL's retrieved are user_id's in the file
    "at-hikers.txt" who do not already appear in the storage directory as a .json file.
@return hiker_urls -A list of hiker journal entry url's that have yet to be scraped.
"""
def get_hiker_urls():
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

def extract_hiker_id(hiker_relative_url):
    hiker_url_start = str.find(hiker_relative_url, "trailname=", 0, len(hiker_relative_url)) + len("trailname=")
    hiker_id = hiker_relative_url[hiker_url_start:len(hiker_relative_url)]
    return int(hiker_id)

"""
parse_hiker_info -Parses the Hiker's information (id, name, trail_name, etc...) using Scrapy Selectors and urllib.
@param about_url -The url for the hiker's about page.
@param identifier -The unique identifier to be assigned to this hiker.
@return hiker -A dictionary containing the hiker's information.
"""
def parse_hiker_info(about_url):
    print("Parsing Hiker Info from: %s" % about_url)
    hiker = {
        'identifier': extract_hiker_id(hiker_relative_url=about_url),
        'about_url': about_url,
        'journal_url': extract_first_journal_url(str.replace(about_url, "about", "entry"))
    }
    with contextlib.closing(urlopen(about_url)) as fp:
        source = fp.read()
    hiker_name_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]/table//tr[2]/td//font[2]"
    hiker_name = Selector(text=source).xpath(hiker_name_xpath).extract()[0]
    hiker_name_start = str.find(hiker_name, "-", 0, len(hiker_name))
    hiker_name_end = str.find(hiker_name, "<", hiker_name_start, len(hiker_name))
    hiker_name = hiker_name[hiker_name_start + 1:hiker_name_end]
    hiker_name = str.strip(hiker_name, " ")
    hiker['name'] = hiker_name
    hiker_trail_name_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]/table//tr[2]/td//font[1]/b"
    hiker_trail_name = Selector(text=source).xpath(hiker_trail_name_xpath).extract()[0]
    hiker_trail_name_start = str.find(hiker_trail_name, ">", 0, len(hiker_trail_name))
    hiker_trail_name_end = str.find(hiker_trail_name, "<", hiker_trail_name_start, len(hiker_trail_name))
    hiker_trail_name = hiker_trail_name[hiker_trail_name_start + 1:hiker_trail_name_end]
    hiker['trail_name'] = hiker_trail_name
    # TODO: Write code to get hiker start_date, end_date, and dir
    return hiker

"""
extract_first_journal_url -Retrieves the url of the first journal entry.
@param journal_url -The pre-existing url that links to a random journal entry (usually the first).
@param response -The Scrapy HtmlResponse object of the presumed first journal entry.
@return first_entry_url -The URL of the first journal entry.
"""
def extract_first_journal_url(journal_url):
    domain = "http://www.trailjournals.com/"
    with contextlib.closing(urlopen(journal_url)) as fp:
        source = fp.read()
    first_entry_url_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]/table//tr[1]"
    first_entry_url = Selector(text=source).xpath(first_entry_url_xpath + "//a[contains(text(), 'First')]")
    if first_entry_url:
        first_entry_url = first_entry_url.extract()[0]
        # Not on the first journal page. Record the first entry url.
        url_start = first_entry_url.find("href=") + len("href=\"")
        first_entry_url = first_entry_url[url_start:len(first_entry_url)]
        first_entry_url = first_entry_url[0:first_entry_url.find("\"")]
        return domain + first_entry_url
    # Already on the first journal page.
    return journal_url

"""
extract_journal_entry_date -Uses Scrapy xpath Selectors to obtain the date of the current journal entry.
@param entry_source -The urllib file pointer containing the journal entry.
@return entry_date -The date that the current journal entry was made, None if no date was provided.
"""
def extract_entry_date(entry_source):
    entry_date_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]/table//tr[2]/td/div/font/i"
    entry_date = Selector(text=entry_source).xpath(entry_date_xpath).extract()[0]
    if entry_date:
        entry_date = str.replace(entry_date, "<i>", "")
        entry_date = str.replace(entry_date, "</i>", "")
        return entry_date
    else:
        return None

"""
extract_next_entry_url -Uses Scrapy xpath Selectors to obtain the url for the next journal entry.
@param entry_source -The urllib file pointer containing the journal entry.
@return next_entry_url -The url for the next journal entry if present, None otherwise.
"""
def extract_next_entry_url(domain, entry_source):
    navbar_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]//table[1]//tr[1]//td[1]"
    next_entry_url = Selector(text=entry_source).xpath(navbar_xpath + "//*[contains(text(), 'Next')]")
    if next_entry_url:
        next_entry_url = next_entry_url.extract()[0]
        next_entry_url = next_entry_url[str.find(next_entry_url, "id", 0, len(next_entry_url)):len(next_entry_url)]
        next_entry_url = next_entry_url[0:str.find(next_entry_url, ">")]
        next_entry_url = str.strip(next_entry_url, "\"")
        next_entry_url = "entry.cfm?" + next_entry_url
        next_entry_url = domain + next_entry_url
        return next_entry_url
    else:
        return None

"""
extract_prev_entry_url -Uses Scrapy xpath Selectors to obtain the url for the previous journal entry.
@param entry_source -The urllib file pointer containing the journal entry.
@return next_entry_url -The url for the previous journal entry if present, None otherwise.
"""
def extract_prev_entry_url(domain, entry_source):
    navbar_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]//table[1]//tr[1]//td[1]"
    prev_entry_url = Selector(text=entry_source).xpath(navbar_xpath + "//a[contains(text(), 'Previous')]").extract()[0]
    if prev_entry_url:
        prev_entry_url = prev_entry_url[str.find(prev_entry_url, "id", 0, len(prev_entry_url)):len(prev_entry_url)]
        prev_entry_url = prev_entry_url[0:str.find(prev_entry_url, ">")]
        prev_entry_url = str.strip(prev_entry_url, "\"")
        prev_entry_url = "entry.cfm?" + prev_entry_url
        prev_entry_url = domain + prev_entry_url
        return prev_entry_url
    else:
        return None

"""
extract_entry_destination -Uses Scrapy xpath Selectors to obtain the destination listed in the journal entry.
@param entry_source -The urllib file pointer containing the journal entry.
@return destination -The text entered in the journal for the destination if present, None otherwise.
"""
def extract_entry_destination(entry_source):
    trip_info_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]//table[1]//tr[3]"
    destination = Selector(text=entry_source).xpath(trip_info_xpath + "//td//span[contains(text(), 'Destination')]/following::span[1]")
    if destination:
        destination = destination.extract()[0]
        destination_start = destination.find(">") + len(">")
        destination = destination[destination_start:len(destination)]
        destination = destination[0:destination.find("<")]
        if destination != '':
            return destination
        else:
            return None
    else:
        return None

"""
extract_entry_start_loc -Uses Scrapy xpath Selectors to obtain the start location listed in the journal entry.
@param entry_source -The urllib file pointer containing the journal entry.
@return start_loc -The text enetered in the journal for the starting location if present, None otherwise.
"""
def extract_entry_start_loc(entry_source):
    trip_info_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]//table[1]//tr[3]"
    start_loc = Selector(text=entry_source).xpath(trip_info_xpath + "//td//span[contains(text(), 'Starting Location')]/following::span[1]")
    if start_loc:
        start_loc = start_loc.extract()[0]
        start_loc_start = start_loc.find(">") + len(">")
        start_loc = start_loc[start_loc_start:len(start_loc)]
        start_loc = start_loc[0:start_loc.find("<")]
        if start_loc != '':
            return start_loc
        else:
            return None
    else:
        return None

"""
extract_entry_trip_mileage -Uses Scrapy xpath Selectors to obtain the total trip mileage listed in the journal entry.
@param entry_source -The urllib file pointer containing the journal entry.
@return entry_trip_mileage -The float entered in the journal for the trip mileage if present, None otherwise.
"""
def extract_entry_trip_mileage(entry_source):
    trip_info_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]//table[1]//tr[3]"
    entry_trip_mileage = Selector(text=entry_source).xpath(trip_info_xpath + "//td//span[contains(text(), 'Trip Miles')]/following::span")
    if entry_trip_mileage:
        entry_trip_mileage = entry_trip_mileage.extract()[0]
        mileage_start = entry_trip_mileage.find(">") + len(">")
        entry_trip_mileage = entry_trip_mileage[mileage_start:len(entry_trip_mileage)]
        entry_trip_mileage = entry_trip_mileage[0:entry_trip_mileage.find("<")]
        if entry_trip_mileage != '':
            return float(entry_trip_mileage)
        else:
            return None
    else:
        return None

"""
extract_entry_day_mileage -Uses Scrapy xpath Selectors to obtain the daily trip mileage listed in the journal entry.
@param entry_source -The urllib file pointer containing the journal entry.
@return day_mileage -The float entered in the journal for the trip mileage if present, None otherwise.
"""
def extract_entry_day_mileage(entry_source):
    trip_info_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]/table[1]"
    day_mileage = Selector(text=entry_source).xpath(trip_info_xpath + "//td//span[contains(text(), 'Today')]/following::span")
    if day_mileage:
        day_mileage = day_mileage.extract()[0]
        day_mileage_start = str.find(day_mileage, ">") + len(">")
        day_mileage = day_mileage[day_mileage_start:len(day_mileage)]
        day_mileage = day_mileage[0:day_mileage.find("<")]
        if day_mileage != '':
            return float(day_mileage)
        else:
            return None
    else:
        return None

def extract_entry(entry_source):
    trip_info_xpath = "/html/body/table//tr[4]/td/table/tr//td[2]/table[1]"
    entry = Selector(text=entry_source).xpath(trip_info_xpath + "//td//blockquote")
    if entry:
        entry = entry.extract()[0]
        entry_start = str.find(entry, "<blockquote>") + len("<blockquote>")
        entry = entry[entry_start:len(entry)]
        entry = entry[0:str.find(entry, "<!---")]
        entry = str.replace(entry, "\r", "")
        entry = str.replace(entry, "\n", "")
        entry = str.replace(entry, "\t", "")
        entry = str.replace(entry, "<br>", " ")
        entry = str.replace(entry, "\xa0", "")
        entry = str.strip(entry, " ")
        if entry != '':
            return entry
        else:
            return None

"""
has_next_entry -Given a hiker journal entry, determines whether there is a next journal entry.
@param hiker_journal_entry -A pre-recorded hiker journal entry from which to judge continuity.
@return boolean -True if there is a following entry, false otherwise.
"""
def has_next_entry(hiker_journal_entry):
    if hiker_journal_entry['next_entry'] is None:
        return False
    else:
        return True

"""
parse_hiker_journal -Parses the hiker's unvalidated trail journal entry by entry, using Scrapy Selectors and urllib.
@param journal_url -A url pointing to the FIRST trail journal entry for this hiker.
@return hiker_journal -An Ordered Dictionary of journal entries arranged chronologically.
"""
def parse_hiker_journal(journal_url):
    domain = "http://www.trailjournals.com/"
    print("Parsing Hiker Trail Journal from: %s" % journal_url)
    hiker_journal = collections.OrderedDict()
    entry_num = 0
    # Parse the first journal entry and record:
    with contextlib.closing(urlopen(journal_url)) as fp:
        first_entry_source = fp.read()
    hiker_journal[entry_num] = {
        'date': extract_entry_date(entry_source=first_entry_source),
        'trip_mileage': extract_entry_trip_mileage(entry_source=first_entry_source),
        'day_mileage': extract_entry_day_mileage(entry_source=first_entry_source),
        'start_loc': extract_entry_start_loc(entry_source=first_entry_source),
        'dest': extract_entry_destination(entry_source=first_entry_source),
        'entry': extract_entry(entry_source=first_entry_source),
        'next_entry': extract_next_entry_url(domain=domain, entry_source=first_entry_source),
        'prev_entry': None
    }
    while has_next_entry(hiker_journal[entry_num]):
        current_entry = hiker_journal[entry_num]
        with contextlib.closing(urlopen(current_entry['next_entry'])) as fp:
            next_entry_source = fp.read()

        entry_num += 1
        hiker_journal[entry_num] = {
            'date': extract_entry_date(entry_source=next_entry_source),
            'trip_mileage': extract_entry_trip_mileage(entry_source=next_entry_source),
            'day_mileage': extract_entry_day_mileage(entry_source=next_entry_source),
            'start_loc': extract_entry_start_loc(entry_source=next_entry_source),
            'dest': extract_entry_destination(entry_source=next_entry_source),
            'entry': extract_entry(entry_source=next_entry_source),
            'next_entry': extract_next_entry_url(domain=domain, entry_source=next_entry_source),
            'prev_entry': extract_prev_entry_url(domain=domain, entry_source=next_entry_source)
        }
    return hiker_journal

def write_hiker(hiker):
    storage_location = "C:/Users/Chris/Documents/GitHub/ATS/Data/Hiker_Data"
    hiker_fname = storage_location + "/" + str(hiker['identifier']) + ".json"
    working_dir = os.getcwd()
    if os.path.isdir(storage_location):
        os.chdir(storage_location)
        with open(hiker_fname, 'w') as fp:
            json.dump(hiker, fp)
        print("Hiker id: %d now logged.\n" % hiker['identifier'])
    os.chdir(working_dir)

def main():
    hiker_urls = get_hiker_urls()
    hiker_num = 0
    hikers = {}
    for url in hiker_urls:
        hiker = parse_hiker_info(about_url=url)
        print("Done. Hiker: %s" % hiker)
        start_time = time.clock()
        hiker['journal'] = parse_hiker_journal(journal_url=hiker['journal_url'])
        end_time = time.clock()
        print("Done. Journal data obtained in %f seconds. \nFirst Entry: %s" % ((end_time - start_time), hiker['journal'][0]))
        write_hiker(hiker)
        hikers[hiker['identifier']] = hiker
        hiker_num += 1

if __name__ == '__main__':
    main()
