"""
UserValidator.py
A test suite for ensuring the web scraper is writing data to hard drive correctly.
@Author: Chris Campell
@Version: 6/8/2016
"""
from selenium import webdriver
import json
from pprint import pprint

driver = webdriver.Firefox()

def fileLineCount(fname):
    with open(fname) as file:
        for i, l in enumerate(file):
            pass
        return i + 1

'''
    testDataStore -Performs data extraction on the written json file to ensure integrity.
    :param json_fname - The name of the json file to extract data from and validate.
'''
def testDataStore(json_fname):
    with open(json_fname) as data_file:
        data = json.load(data_file)
    pprint(data)

# Test Suite Driver:
num_hikers = fileLineCount("at-hikers.txt")
print("Current Number of Unique AT Hikers Logged: %d" % num_hikers)
testDataStore("hiker-data.json")



'''
journal_name_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/div/font"
start_url = "http://www.trailjournals.com/entry.cfm?trailname="
# Iterate through every user in the dump and verify that they are AT hikers.
for line in iter(user_dump):
    driver.get(start_url + line)
    if ("Appalachian Trail" in driver.find_element_by_xpath(journal_name_xpath).text):
        at_hikers.write(line)
    else:
        print("User %d is not an AT hiker." % line)
at_hikers.close()
user_dump.close()
'''
