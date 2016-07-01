"""
HikerRecorder.py
Records every hikers GPS data in a CSV for upload to Google Fusion Tables.
@Author: Chris Campell
@Version: 6/29/2016
"""
import sys
import os.path
import json
import copy
from collections import OrderedDict

class HikerRecorder(object):

    def __init__(self):
        pass

    def writeHiker(self, output_file):
        pass

"""
sortHikerJournal -Takes an unsorted hiker trail journal and returns a journal sorted by entry number.
@param hiker_journal -An unsorted hiker journal dictionary.
@return sorted_journal -The hiker journal sorted by entry number.
"""
def sortHikerJournal(hiker_journal):
    # TODO: fix below code. Not sorting by journal keys despite integer conversion and use of sorted()
    sorted_journal = OrderedDict()
    sorted_int_journal = {int(k):v for k,v in hiker_journal.items()}
    for key in sorted(sorted_int_journal.keys()):
        sorted_journal[key] = hiker_journal[str(key)]
    return sorted_journal

"""
isValidStorageLocation -Determines if the provided file path is recognizable by the OS.
@param storage_location -The file path to validate.
@return boolean -True if valid file path, false otherwise.
"""
def isValidStorageLocation(storage_location):
     if not os.path.isdir(storage_location):
        print("HIKER RECORDER: Hiker Storage Location Not Recognized by OS!")
        return False
     else:
         return True

"""
convertToCSV -Converts the hiker journal to a csv friendly format, removing pre-existing commas.
@param hiker_journal -The journal to be converted to a csv friendly format.
@return csv_hiker_journal -An identical hiker journal now in csv format (commas removed). 
"""
def convertToCSV(hiker_journal):
    csv_hiker_journal = copy.deepcopy(hiker_journal)
    csv_hiker_journal['date'] = csv_hiker_journal['date'].replace(",", " ")
    return csv_hiker_journal

def main(cmd_args):
    storage_location = "C:/Users/Chris/Documents/GitHub/ATS/Data/Hiker_Data"
    if not isValidStorageLocation(storage_location=storage_location):
        exit(-1)
    # Open the necessary files:
    at_hikers = open("at-hikers.txt", 'r')
    hiker_csv = open('hikers.csv', 'w')
    # Write CSV header:
    hiker_csv.write("id,entry,date,start,dest,day_mileage,trip_mileage\n")

    for line in iter(at_hikers):
        hiker_fname = storage_location + "/" + str.strip(line, '\n') + ".json"
        if not os.path.isfile(hiker_fname):
            print("HIKER RECORDER: Hiker File: %s not found." % hiker_fname)

        with open(hiker_fname, 'r') as fp:
            hiker_data = json.load(fp=fp)
            # hiker_csv.write(str(hiker_data['identifier']) + ",")
            hiker_journal = hiker_data['journal']
            hiker_journal = sortHikerJournal(hiker_journal=hiker_journal)
            hiker_journal = convertToCSV(hiker_journal)
            hiker_id = hiker_data['identifier']
            for key, value in hiker_journal.items():
                hiker_csv.write(str(hiker_id) + "," + str(key) + "," + value['date'] + "," + value['start_loc'] + "," + value['dest'] + "," + str(value['day_mileage']) + "," + str(value['trip_mileage']) + "\n")
            hiker_csv.close()
    at_hikers.close()


if __name__ == '__main__':
    main(sys.argv)