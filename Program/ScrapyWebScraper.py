"""
ScrapyWebScraper.py
Scrapes the Appalachian trail journal website for relevant information using the Scrapy package.
 @Author: Chris Campell
 @Version: 7/5/2016
"""

import os
import sys
import Scrapy

class ScrapyWebScraper(object):

    def __init__(self):
        start_url = "http://www.trailjournals.com/entry.cfm?trailname="
        at_hikers = open("at-hikers.txt", 'r')
        storage_location = "C:/Users/Chris/Documents/GitHub/ATS/Data/Hiker_Data"
        for line in iter(at_hikers):
            hiker_fname = storage_location + "/" + str.strip(line, '\n') + ".json"
            if not os.path.isfile(hiker_fname):
                hiker_url = start_url + line
            else:
                print("Hiker id: %d has already been logged." % int(line))
        at_hikers.close()

def main(cmd_args):
    pass

if __name__ == '__main__':
    main(sys.argv)


