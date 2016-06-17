"""
WebScraper.py
TODO: file description
@Author: Chris Campell
@Version: 6/3/2016
"""
import sys
import json
from selenium import webdriver
import os.path
import itertools
from timeit import timeit
from json import JSONEncoder

driver = webdriver.Firefox()
num_hikers = 0
hikers = []
hiker_identifiers = set([])

"""
TODO: class descriptor.
"""
class Hiker(object):
    """
    __init__ -Constructor for objects of type Hiker.
    @param self -A reference to an instance of the Hiker class.
    @param identifier -A unique hiker identifier read from the at-hikers file.
    @param name -The hiker's birth name.
    @param trail_name -The hiker's trail name.
    @param start_date -The date the hiker supposedly started the trail.
    @param end_date -The date the hiker has finished (or will finish) the trail.
    @param journal -The hiker's trail journal.
    """
    def __init__(self, identifier, name=None, trail_name=None, start_date=None, end_date=None, journal={}):
        self.identifier = identifier
        self.name = name
        self.trail_name = trail_name
        self.start_date = start_date
        self.end_date = end_date
        self.journal = journal

    """
    addJournalEntry -Adds a new entry to the hiker's pre-existing trail journal.
    @param self -A reference to the instance of the Hiker class.
    @param entry_number -The journal's entry number.
    @param starting_location -The starting location as detailed in that day's journal entry.
    @param destination -The desired ending location as detailed in that day's journal entry.
    @param day_mileage -The day's trip mileage as detailed in that day's journal entry.
    @param trip_mileage -The total trip mileage as detailed in that day's journal entry.
    @param date -The date provided for that day's journal entry.
    """
    def addJournalEntry(self, entry_number, starting_location, destination, day_mileage, trip_mileage, date, text=None):
        if self.journal is None:
            self.journal = {'ENO': entry_number, 'dest': destination, 'start_loc': starting_location, 'day_mileage': day_mileage, 'trip_mileage': trip_mileage, 'date': date, 'text': text}
        else:
            self.journal[str(entry_number)] = {'dest': destination, 'start_loc': starting_location, 'day_mileage': day_mileage, 'trip_mileage': trip_mileage, 'date': date, 'text': text}

    """
    removeJournalEntry -Removes a pre-existing journal entry from the hiker's trail journal.
    @param self -A reference to the instance of the Hiker class.
    @param entry_number -The entry number of the journal to be removed.
    """
    def removeJournalEntry(self, entry_number):
        del self.journal[str(entry_number)]

    """
    setHikerName -Sets the name associated with this instance of Hiker.
    @param self -A reference to the instance of the Hiker class.
    @param hiker_name -The desired birth name to be set.
    """
    def setHikerName(self, hiker_name):
        self.name = hiker_name

    """
    """
    def setHikerTrailName(self, trail_name):
        self.trail_name = trail_name

    """
    """
    def setHikerTrailDirection(self, direction):
        self.direction = direction

    """
    """
    def setHikerStartDate(self, starting_date):
        self.start_date = starting_date

    """
    """
    def setHikerEndDate(self, estimated_end_date):
        self.end_date = estimated_end_date

"""
recordHikerInfo - Scrapes and records identifying hiker information such as name,
    trail name, start_date, end_date and their unique hiker id.
@param hiker_id -The hiker's unique identifier.
@param journal_url -The url to the first entry of the hiker's trail journal.
"""
def recordHikerInfo(hiker_id, journal_url):
    driver.get(journal_url)
    about_url_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[1]/table[1]/tbody/tr/td/table[3]/tbody/tr[4]/td/a"
    try:
        about_url = driver.find_element_by_xpath(about_url_xpath).get_attribute("href")
        driver.get(about_url)
    except:
        hiker = Hiker(hiker_id)
        return hiker
    # Attempt to get hiker information:
    hiker_name_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table/tbody/tr[2]/td/font[2]"
    hiker_trail_name_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table/tbody/tr[2]/td/font[1]"
    hiker_info_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table/tbody"

    try:
        hiker_name = driver.find_element_by_xpath(hiker_name_xpath).text
        hiker_name = str.strip(hiker_name, ' - ')
    except:
        # hiker name not provided.
        hiker_name = None
        pass
    try:
        hiker_trail_name = driver.find_element_by_xpath(hiker_trail_name_xpath).text
    except:
        # hiker trail name not provided.
        hiker_trail_name = None
        pass
    try:
        hiker_start_date_neighbor_xpath = hiker_info_xpath + "//*[contains(text(), 'Started:')]"
        hiker_start_date_xpath = hiker_start_date_neighbor_xpath + "/following-sibling::td[1]"
        hiker_start_date = driver.find_element_by_xpath(hiker_start_date_xpath).text
    except:
        # hiker start date not provided.
        hiker_start_date = None
        pass
    try:
        hiker_end_date_xpath = hiker_info_xpath + "//*[contains(text(), 'Started:')]/following-sibling::td[1]"
        hiker_end_date = driver.find_element_by_xpath(hiker_end_date_xpath).text
    except:
        # hiker end date not provided.
        hiker_end_date = None
        pass
    # Add the hiker data to the list of hikers. Hiker will be created with hiker.journal = {}.
    hiker = Hiker(identifier=hiker_id, name=hiker_name,
                  trail_name=hiker_trail_name, start_date=hiker_start_date, end_date=hiker_end_date)
    # Update the hiker identifiers list to reflect that this hiker's non-journal information has been logged.
    hiker_identifiers.add(hiker_id)
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

def writeHiker(hiker):
    hiker_json = {'identifier': hiker.identifier, 'name': hiker.name,
                  'trail_name': hiker.trail_name, 'start_date': hiker.start_date,
                  'end_date': hiker.end_date, 'journal': hiker.journal}
    write_dir = "C:/Users/Chris/Documents/GitHub/ATS/Data/Hiker_Data"
    working_dir = os.getcwd()
    # validate write directory:
    if os.path.isdir(write_dir):
        # write directory recognized. Create new file.
        os.chdir(write_dir)
        json_fname = write_dir + "/" + str(hiker.identifier) + ".json"
        with open(json_fname, 'w') as fp:
            json.dump(hiker_json, fp)
        print("Hiker id: %d now logged." % hiker.identifier)
    else:
        print("ERROR: Write directory not specified correctly. Hiker %d (%s) not saved." % hiker.identifier, hiker.name)
    os.chdir(working_dir)

'''
parseHikerJournal -Scrapes and records each journal entry on the website for a given hiker.
@param hiker -A hiker object already populated with identifying information.
@param journal_url -The URL of the hiker's journal on the website.
'''
def parseHikerJournal(hiker, journal_url):
    driver.get(journal_url)
    hiker_nav_bar_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table[1]/tbody/tr[1]/td"
    try:
        first_entry = driver.find_element_by_xpath(hiker_nav_bar_xpath + "/a[position()=1]")
        first_entry_url = first_entry.get_attribute("href")
    except:
        hiker.journal = {}
        return hiker
    # Determine if already on the first entry of the journal:
    if first_entry.text != 'Next':
        driver.get(first_entry_url)

    last_entry = driver.find_element_by_xpath(hiker_nav_bar_xpath + "/a[position()=2]")
    last_entry_url = last_entry.get_attribute("href")
    next_entry = driver.find_element_by_xpath(hiker_nav_bar_xpath + "/a[position()=1]")
    next_entry_url = next_entry.get_attribute("href")
    journal_date_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table[1]/tbody/tr[2]/td/div/font/i"
    entry_number = 0
    journal_index = 0
    # check to see if title was provided...
    trail_info_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table[1]/tbody/tr[4]"
    trail_info_xpath2 = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table[1]/tbody/tr[3]"
    journal_entry_xpath2 = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table[1]/tbody/tr[5]"
    journal_entry_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table[1]/tbody/tr[6]"
    trail_info = driver.find_elements_by_xpath(trail_info_xpath)
    if 'First Previous Next Last' not in trail_info[0].text:
        destination_xpath = trail_info_xpath2 + "/td[2]/span[2]"
        start_loc_xpath = trail_info_xpath2 + "/td[2]/span[4]"
        day_mileage_xpath = trail_info_xpath2 + "/td[3]/span[2]"
        trip_mileage_xpath = trail_info_xpath2 + "/td[3]/span[4]"
        journal_entry_xpath = journal_entry_xpath2 + "/td/blockquote"
    else:
        destination_xpath = trail_info_xpath + "/td[2]/span[2]"
        start_loc_xpath = trail_info_xpath + "/td[2]/span[4]"
        day_mileage_xpath = trail_info_xpath + "/td[3]/span[2]"
        trip_mileage_xpath = trail_info_xpath + "/td[3]/span[4]"
        journal_entry_xpath = journal_entry_xpath + "/td/blockquote"

    while next_entry_url != last_entry_url:
        try:
            destination = driver.find_element_by_xpath(destination_xpath)
            destination = destination.text
        except Exception:
            # no starting location provided.
            destination = None
            pass
        try:
            start_loc = driver.find_element_by_xpath(start_loc_xpath)
            start_loc = start_loc.text
        except:
            # no starting location provided.
            start_loc = None
            pass
        try:
            day_mileage = driver.find_element_by_xpath(day_mileage_xpath)
            day_mileage = float(day_mileage.text)
        except:
            # no day mileage provided.
            day_mileage = None
            pass
        try:
            trip_mileage = driver.find_element_by_xpath(trip_mileage_xpath)
            trip_mileage = float(trip_mileage.text)
        except:
            # no trip mileage provided
            trip_mileage = None
            pass
        try:
            journal_date = driver.find_element_by_xpath(journal_date_xpath)
            journal_date = journal_date.text
        except:
            # journal entry not dated.
            journal_date = None
            pass
        try:
            journal_entry = driver.find_element_by_xpath(journal_entry_xpath)
            journal_entry = journal_entry.text
        except:
            # journal entry not provided.
            journal_entry = None
            pass

        if journal_index != 0:
            # TODO: parse other page content here.
            next_entry = driver.find_element_by_xpath(hiker_nav_bar_xpath + "/a[position()=3]")
            next_entry_url = next_entry.get_attribute("href")
        else:
            next_entry = driver.find_element_by_xpath(hiker_nav_bar_xpath + "/a[position()=1]")
            next_entry_url = next_entry.get_attribute("href")
        # if all fields are blank; don't bother storing.
        if start_loc is not None and destination is not None:
            hiker.addJournalEntry(entry_number=entry_number, starting_location=start_loc, destination=destination, day_mileage=day_mileage, trip_mileage=trip_mileage, date=journal_date, text=journal_entry)
            entry_number += 1
        journal_index += 1
        driver.get(next_entry_url)
    return hiker

'''
TODO: function definition.
'''
def isFirstPage(hiker_url):
    hiker_nav_bar_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table[1]/tbody/tr[1]/td"
    first_link = driver.find_element_by_xpath(hiker_nav_bar_xpath + "/a[position()=1]")
    first_link_url = first_link.get_attribute("href")
    return first_link.text == 'Next'

def getFirstEntry(hiker_url):
    # TODO: method body.
    hiker_nav_bar_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table[1]/tbody/tr[1]/td"
    first_entry = driver.find_element_by_xpath(hiker_nav_bar_xpath + "/a[position()=1]")
    first_entry_url = first_entry.get_attribute("href")

'''
TODO: method body.
'''
def main(args):
    # main loop checks Data/Hiker_Data for presence of [hiker_id].json file. If file is absent then parse necessary data.
    start_url = "http://www.trailjournals.com/entry.cfm?trailname="
    at_hikers = open("at-hikers.txt", 'r')
    storage_location = "C:/Users/Chris/Documents/GitHub/ATS/Data/Hiker_Data"
    for line in iter(at_hikers):
        hiker_fname = storage_location + "/" + str.strip(line, '\n') + ".json"
        if not os.path.isfile(hiker_fname):
            hiker_url = start_url + line
            hiker = recordHikerInfo(hiker_id=int(line), journal_url=hiker_url)
            hiker = parseHikerJournal(hiker, journal_url=hiker_url)
            writeHiker(hiker)
        else:
            print("Hiker id: %d has already been logged." % int(line))
    at_hikers.close()

if __name__ == '__main__':
    print("CODER: Resume hiker information validation at Hiker id: 4")
    main(sys.argv)
    # TODO: Hikers are having email addresses and other extranous information entered in the start_date field.
    #       TODO: Need to figure out how to dynamically search for text and get following element. Or attempt conversion to python DATE_TIME object.
    # print("Added " + str(len(hiker_identifiers)) + " unique hiker id's")
    # print(hiker_identifiers)
    # timeit(parseHikers(hiker_identifiers))
    # parseHikers(hiker_identifiers)
