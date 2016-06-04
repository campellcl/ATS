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
TODO: class descriptors.
"""
class Hiker:
    name = ''
    trail_name = ''
    direction = ''
    start_date = None
    end_date = None
    identifier = None
    journal = None



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
    hiker = {'identifier': identifier}
    driver.get(journal_url)
    hiker_nav_bar_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table[1]/tbody/tr[1]/td"
    hiker_nav_bar = driver.find_elements_by_xpath(hiker_nav_bar_xpath)
    first_entry = driver.find_element_by_xpath(hiker_nav_bar_xpath + "/a[position()=1]")
    driver.get(first_entry.get_attribute("href"))
    last_entry = driver.find_element_by_xpath(hiker_nav_bar_xpath + "/a[position()=2]")
    last_entry_url = last_entry.get_attribute("href")
    next_entry = driver.find_element_by_xpath(hiker_nav_bar_xpath + "/a[position()=1]")
    next_entry_url = next_entry.get_attribute("href")
    entry_number = 0
    trail_info_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table[1]/tbody/tr[4]"
    destination_xpath = trail_info_xpath + "/td[2]/span[2]"
    start_loc_xpath = trail_info_xpath + "/td[2]/span[4]"
    day_mileage_xpath = trail_info_xpath + "/td[3]/span[2]"
    trip_mileage_xpath = trail_info_xpath + "/td[3]/span[4]"

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
        if entry_number != 0:
            # TODO: parse other page content here.
            next_entry = driver.find_element_by_xpath(hiker_nav_bar_xpath + "/a[position()=3]")
            next_entry_url = next_entry.get_attribute("href")
        else:
            hiker['journal'] = {'ENO': 0}
        hiker['journal']['dest'] = destination
        hiker['journal']['start_loc'] = start_loc
        hiker['journal']['day_mileage'] = day_mileage
        hiker['journal']['trip_mileage'] = trip_mileage
        entry_number += 1
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
