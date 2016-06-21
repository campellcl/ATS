"""
UserValidator.py
A test suite for ensuring the web scraper is writing data to hard drive correctly.
@Author: Chris Campell
@Version: 6/8/2016
"""
from sys import argv
from selenium import webdriver
import json
import os.path
from pprint import pprint
from geopy import geocoders
from geopy.geocoders import GoogleV3

class HikerValidator(object):
    working_dir = os.getcwd()

    def __init__(self, hiker_data_dir):
        if hiker_data_dir is None:
            print("ERROR: A directory must be provided for hiker validation")
        elif not os.path.isdir(hiker_data_dir):
            print("ERROR: A valid directory must be provided for hiker validation")
        else:
            self.hiker_data_dir = hiker_data_dir
        self.shelters = None

    def validateHiker(self, hiker):
        self.validateShelters(hiker)

    def validateHikers(self):
        storage_location = "C:/Users/Chris/Documents/GitHub/ATS/Data/Hiker_Data"

        with open("at-hikers.txt", 'r') as fp:
            for line in iter(fp):
                hiker_file_name = self.hiker_data_dir + "/" + str.strip(line, '\n') + ".json"
                if not os.path.isfile(hiker_file_name):
                    print("ERROR: Requested hiker file: %s not found." % hiker_file_name)
                    break
                else:
                    with open(hiker_file_name, 'r') as hiker_file:
                        hiker_data = json.load(hiker_file)
                        # pprint(hiker_data)
                        self.validateHiker(hiker_data)

    def populateShelters(self):
        self.shelters = []
        at_shelter_path = "C:/Users/Chris/Documents/GitHub/ATS/Data/AT_Conservancy_Data/AT_Shelters/AT_Shelters.csv"
        fp = open(at_shelter_path, 'r')
        line_num = 0
        for line in iter(fp):
            if not line_num == 0:
                self.shelters.append(str.split(line, sep=",")[1])
            line_num += 1
        fp.close()
        # print("Total Number of Shelters: %d" %len(self.shelters))

    def geocodeShelters(self):
        geocoder = GoogleV3()
        # TODO: Geocode the entire csv file using Geopy package. Then begin validation.
        for shelter in self.shelters:
            geocoded_shelter = geocoder.reverse("40.782489972, -75.618317351")
            # TODO: shelter when geocoded is a list of possible locations. Choose one using .contains(substring(Appalachian Trail))
            print(geocoded_shelter)
            geocoded_shelter = geocoder.geocode(shelter)
            print(geocoded_shelter)

    def validateShelters(self, hiker):
        # compare every shelter by converting the google fusion table data to lower case string and then execute substring comparison.
        # delete the entries that are unvalidated? Might still need to retain for distance estimation using day mileage.
        if self.shelters is None:
            self.populateShelters()
            self.geocodeShelters()
        hiker_journal = hiker['journal']
        geolocator = GoogleV3()
        for i in range(len(hiker_journal) - 1):
            start_location = hiker_journal[str(i)]['start_loc']
            dest_location = hiker_journal[str(i)]['dest']
            is_valid_start = False
            is_valid_end = False
            start_loc = geolocator.geocode(query=start_location)
            end_loc = geolocator.geocode(query=dest_location)

            for shelter in self.shelters:
                shelter_name_lowercase = str.lower(shelter)
                if str.lower(hiker_journal[str(i)]['start_loc']) in shelter_name_lowercase:
                    # Shelter validated to be an entry in the AT_Shelters.csv file.
                    hiker_journal[str(i)]['validated'] = True

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
    storage_dir = "C:/Users/Chris/Documents/GitHub/ATS/Data/Hiker_Data"
    fname = storage_dir + "/" + json_fname
    working_dir = os.getcwd()
    os.chdir(storage_dir)
    with open(fname, "r") as data_file:
        data = json.load(data_file)
    pprint(data)
    os.chdir(working_dir)

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

def main(cmd_args):
    num_hikers = fileLineCount("at-hikers.txt")
    print("Current Number of Unique AT Hikers Logged: %d" % num_hikers)
    hikerValidator = HikerValidator("C:/Users/Chris/Documents/GitHub/ATS/Data/Hiker_Data")
    hikerValidator.validateHikers()
if __name__ == '__main__':
    main(argv)