"""
WebScraper.py
TODO: file description
@Author: Chris Campell
@Version: 6/3/2016
"""
import sys
from selenium import webdriver
from timeit import timeit

driver = webdriver.Firefox()
num_hikers = 0
hikers = []
hiker_identifiers = set([])

"""
TODO: class descriptor.
"""
class Hiker:
    # TODO: get help overloading the constructor with named variables as in below:
    '''
    def __init__(self, identifier, name, trail_name, direction, start_date, end_date, journal):
        self.identifier = identifier
        self.name = name
        self.trail_name = trail_name
        self.direction = direction
        self.start_date = start_date
        self.end_date = end_date
        self.journal = journal
    '''

    # TODO: Is the below parameterization a correct overloading of the constructor above? Will it work with only 'identifier' as an argument?
    def __init__(self, identifier, **kwargs):
        self.identifier = identifier
        self.journal = {}
        for key, value in kwargs.items():
            self.key = value

    def addJournalEntry(self, entry_number, starting_location, destination, day_mileage, trip_mileage):
        if self.journal == None:
            self.journal = {'ENO': entry_number, 'dest': destination, 'start_loc': starting_location, 'day_mileage': day_mileage, 'trip_mileage': trip_mileage}
        else:
            self.journal[str(entry_number)] = {'dest': destination, 'start_loc': starting_location, 'day_mileage': day_mileage, 'trip_mileage': trip_mileage}

    def removeJournalEntry(self, entry_number):
        del self.journal[str(entry_number)]

    def setHikerName(self, hiker_name):
        self.name = hiker_name

    def setHikerTrailName(self, trail_name):
        self.trail_name = trail_name

    def setHikerTrailDirection(self, direction):
        self.direction = direction

    def setHikerStartDate(self, starting_date):
        self.start_date = starting_date

    def setHikerEndDate(self, estimated_end_date):
        self.end_date = estimated_end_date


def getHikerInfo(trail_name, hiker_string):
    hiker_info = hiker_string.split("\n")
    hiker_name = ""
    journal_url = ""
    start_date = ""
    finish_date = ""
    south_bound = False
    for str in hiker_info:
        if "Started:" in str:
            start_date = str
        elif "Finishing:" in str:
            finish_date = str
        elif "www." in str:
            journal_url = str
        elif str == "Southbound":
            south_bound = True
        else:
            if (str != trail_name and str != ""):
                hiker_name = str
            # either hiker name or trail name provided.
            # handle this information in the parent method.
            pass
    hiker = {'trail_name' : trail_name, 'name' : hiker_name, 'journal_url' : journal_url, 'start_date' : start_date, 'finish_date' : finish_date, 'southbound' : south_bound}
    return hiker

'''
TODO: method body.
'''
def parseHikers(hiker_journal_urls):
    for url in hiker_journal_urls:
        driver.get(url)
        hiker_nav_bar_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table[1]/tbody/tr[1]/td"
        hiker_nav_bar = driver.find_elements_by_xpath(hiker_nav_bar_xpath)
        first_entry = driver.find_element_by_xpath(hiker_nav_bar_xpath + "/a[position()=1]")
        last_entry = ""
        driver.get(first_entry.get_attribute("href"))
        last_entry = driver.find_element_by_xpath(hiker_nav_bar_xpath + "/a[position()=2]")
        last_entry_url = last_entry.get_attribute("href")
        next_entry = driver.find_element_by_xpath(hiker_nav_bar_xpath + "/a[position()=1]")
        next_entry_url = next_entry.get_attribute("href")
        entry_number = 0
        while next_entry_url != last_entry_url:
            if (entry_number == 0):
                # TODO: parse first page content here.
                pass
            else:
                # TODO: parse other page content here.
                next_entry = driver.find_element_by_xpath(hiker_nav_bar_xpath + "/a[position()=3]")
                next_entry_url = next_entry.get_attribute("href")
            entry_number += 1
            driver.get(next_entry_url)
        # TODO: parse the last page content here.

'''
TODO: method body.
'''
def parseHiker(identifier, journal_url):
    hiker = Hiker(identifier=identifier)
    driver.get(journal_url)
    # TODO: Some hiker's trail journals link to their first entry; most don't.
    # TODO: If the hiker's journal links to the first entry then the below code fails.
    hiker_nav_bar_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table[1]/tbody/tr[1]/td"
    hiker_nav_bar = driver.find_elements_by_xpath(hiker_nav_bar_xpath)
    first_entry = driver.find_element_by_xpath(hiker_nav_bar_xpath + "/a[position()=1]")
    first_entry_url = first_entry.get_attribute("href")
    # Determine if already on the first entry of the journal:
    if first_entry.text != 'Next':
        driver.get(first_entry_url)
    last_entry = driver.find_element_by_xpath(hiker_nav_bar_xpath + "/a[position()=2]")
    last_entry_url = last_entry.get_attribute("href")
    next_entry = driver.find_element_by_xpath(hiker_nav_bar_xpath + "/a[position()=1]")
    next_entry_url = next_entry.get_attribute("href")
    entry_number = 0
    journal_index = 0
    trail_info_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table[1]/tbody/tr[4]"
    trail_info_xpath2 = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table[1]/tbody/child::*"
    trail_info = driver.find_elements_by_xpath(trail_info_xpath2)
    destination_xpath = trail_info_xpath + "/td[2]/span[2]"
    start_loc_xpath = trail_info_xpath + "/td[2]/span[4]"
    day_mileage_xpath = trail_info_xpath + "/td[3]/span[2]"
    trip_mileage_xpath = trail_info_xpath + "/td[3]/span[4]"

    # TODO: Error when parsing data as there is a difference in pages.
    # TODO: Page A needs a selection of "../tbody/tr[position()=3]/.." given here: http://www.trailjournals.com/entry.cfm?id=521994
    # TODO: Page B needs a selection of "../tbody/tr[position()=4]/.." given here: http://www.trailjournals.com/entry.cfm?id=521993
    # TODO: Resolve this by checking the len(web_object) returned by driver.
    #       if number <tr> == 3 then grab position()=num_tr-1.

    while next_entry_url != last_entry_url:
        try:
            destination = driver.find_element_by_xpath(destination_xpath)
            destination = destination.text
        except:
            # no starting location provided.
            destination = ''
            pass
        try:
            start_loc = driver.find_element_by_xpath(start_loc_xpath)
            start_loc = start_loc.text
        except:
            # no starting location provided.
            start_loc = ''
            pass
        try:
            day_mileage = driver.find_element_by_xpath(day_mileage_xpath)
            day_mileage = float(day_mileage.text)
        except:
            # no day mileage provided.
            day_mileage = ''
            pass
        try:
            trip_mileage = driver.find_element_by_xpath(trip_mileage_xpath)
            trip_mileage = float(trip_mileage.text)
        except:
            # no trip mileage provided
            trip_mileage = ''
            pass
        if journal_index != 0:
            # TODO: parse other page content here.
            next_entry = driver.find_element_by_xpath(hiker_nav_bar_xpath + "/a[position()=3]")
            next_entry_url = next_entry.get_attribute("href")
        else:
            next_entry = driver.find_element_by_xpath(hiker_nav_bar_xpath + "/a[position()=1]")
            next_entry_url = next_entry.get_attribute("href")

        # if all fields are blank; don't bother storing.
        if start_loc != '' or destination != ''or trip_mileage != '' or day_mileage != '':
            hiker.addJournalEntry(entry_number=entry_number, starting_location=start_loc, destination=destination, day_mileage=day_mileage, trip_mileage=trip_mileage)
            entry_number += 1
        journal_index += 1
        driver.get(next_entry_url)
    # TODO: parse the last page content here.


'''
TODO: method body.
'''
def main(args):
    num_hikers = 0
    start_url = "http://www.trailjournals.com/journals/appalachian_trail/"
    driver.get(start_url)

    hiker_trs_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/div[2]/table/tbody/tr/td[1]/table/tbody/child::*"
    hiker_trs = driver.find_elements_by_xpath(hiker_trs_xpath)
    num_trs_on_page = len(hiker_trs)

    user_table_xpath = \
        "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/div[2]/table/tbody/tr/td[1]/table/tbody"
    hiker_divs_xpath = user_table_xpath + "//tr//td[position()=2]/div"
    entries_xpath = user_table_xpath + "//tr//td[position()=3]/div[position()=1]/a[position()=1]"
    hiker_journal_urls = driver.find_elements_by_xpath(entries_xpath)
    for journal in hiker_journal_urls:
        journal_url = str(journal.get_attribute("href"))
        if journal_url not in hiker_identifiers:
            hiker_identifiers.add(journal_url)
            # TODO: get the hiker's unique number from the journal_url
            hiker_identifier = journal_url.split("=")[1]
            parseHiker(hiker_identifier, journal_url)
        # print(journal_url)

if __name__ == '__main__':
    main(sys.argv)
    # print("Added " + str(len(hiker_identifiers)) + " unique hiker id's")
    # print(hiker_identifiers)
    # timeit(parseHikers(hiker_identifiers))
    # parseHikers(hiker_identifiers)
