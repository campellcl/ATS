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
    for key, value in csv_hiker_journal.items():
        if value['date'] is not None:
            value['date'] = value['date'].replace("\"", "\'")
            value['date'] = ("\"" + value['date'] + "\"")
        else:
            value['date'] = "None"
        if value['start_loc'] is not None:
            value['start_loc']['shelter_name'] = value['start_loc']['shelter_name'].replace("\"", "\'")
            value['start_loc']['shelter_name'] = ("\"" + value['start_loc']['shelter_name'] + "\"")
        else:
            value['start_loc'] = "None"
        if value['dest'] is not None:
            value['dest']['shelter_name'] = value['dest']['shelter_name'].replace("\"", "\'")
            value['dest']['shelter_name'] = ("\"" + value['dest']['shelter_name'] + "\"")
        else:
            value['dest'] = "None"
        '''
        if value['start_loc'] is not None:
            value['start_loc'] = value['start_loc'].replace("\"", "\'")
            value['start_loc'] = ("\"" + value['start_loc'] + "\"")
        else:
            value['start_loc'] = "None"
        if value['dest'] is not None:
            value['dest'] = value['dest'].replace("\"", "\'")
            value['dest'] = ("\"" + value['dest'] + "\"")
        else:
            value['dest'] = "None"
        '''
    return csv_hiker_journal

"""
main -Records every hiker in the hikers.csv file. Adheres to the Google Fusion Table CSV formatting style.
@param cmd_args -Default command line arguments supplied by the system.
"""
def main(cmd_args):
    storage_location = "C:/Users/Chris/Documents/GitHub/ATS/Data/Hiker_Data"
    validated_hiker_location = storage_location + "/Validated_Hikers"
    if not isValidStorageLocation(storage_location=storage_location):
        exit(-1)
    # Open the necessary files:
    at_hikers = open(storage_location + "/at-hikers.txt", 'r')
    hiker_csv = open('hikers.csv', 'w')
    # Write CSV header:
    hiker_csv.write("hiker_id,entry_num,date,start,start_lat,start_lon,dest,dest_lat,dest_lon,day_mileage,trip_mileage\n")
    for filename in os.listdir(validated_hiker_location):
        with open(validated_hiker_location + "/" + filename, 'r') as fp:
            hiker_data = json.load(fp=fp)
        print("Writing Hiker: %s (%s) to CSV file." %(hiker_data['identifier'],hiker_data['trail_name']))
        # hiker_csv.write(str(hiker_data['identifier']) + ",")
        hiker_id = hiker_data['identifier']
        hiker_journal = hiker_data['journal']
        if hiker_journal:
            hiker_journal = sortHikerJournal(hiker_journal=hiker_journal)
            hiker_journal = convertToCSV(hiker_journal)
            for key, value in hiker_journal.items():
                if not value['start_loc'] or value['start_loc'] == "None":
                    start_loc_shelter_name = "None"
                    start_lat = "None"
                    start_lon = "None"
                else:
                    start_loc_shelter_name = value['start_loc']['shelter_name']
                    start_lat = str(value['start_loc']['lat'])
                    start_lon = str(value['start_loc']['lon'])
                if not value['dest'] or value['dest'] == "None":
                    dest_shelter_name = "None"
                    dest_lat = "None"
                    dest_lon = "None"
                else:
                    dest_shelter_name = value['dest']['shelter_name']
                    dest_lat = str(value['dest']['lat'])
                    dest_lon = str(value['dest']['lon'])
                hiker_csv.write(str(hiker_id) + "," + str(key) + "," + value['date'] + ","
                                + start_loc_shelter_name + "," + start_lat + ","
                                + start_lon + "," + dest_shelter_name + "," + dest_lat
                                + "," + dest_lon + "," + str(value['day_mileage']) + "," + str(value['trip_mileage']) + "\n")
        else:
            pass
    else:
        print("HIKER RECORDER: Hiker File: %s not found.")
    hiker_csv.close()
    at_hikers.close()

if __name__ == '__main__':
    main(sys.argv)
