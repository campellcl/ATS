"""
DirectionRecorder.py
Goes through all validated hiker files and updates them with the hiker's direction of travel (northbound vs southbound).
@Author: Chris Campell
@Version: 7/23/2016
"""

import os
import json
import math
import urllib.request
from collections import OrderedDict

class DirectionRecorder(object):
    """
    DirectionRecorder(object) -Reads in already validated hikers determining and assigning the appropriate direction
        of travel (northbound vs southbound).
    @Author: Chris Campell
    @Version: 7/25/2016
    """

    def __init__(self, hiker):
        self.shelter_one = None
        self.shelter_two = None
        hiker['journal'] = self.sort_hiker_journal(hiker_journal=hiker['journal'])
        self.shelter_one = self.get_first_validated_shelter(sorted_journal=hiker['journal'])
        self.shelter_two = self.get_second_validated_shelter(sorted_journal=hiker['journal'])

    """
    get_first_validated_shelter -Returns the first validated/mapped shelter in the hiker journal.
    @param sorted_journal -The hiker journal read from the validated json file sorted by entry number.
    @return shelter_one -The first validated/mapped shelter in the hiker journal.
    """
    def get_first_validated_shelter(self, sorted_journal):
        ordered_entries = list(sorted_journal.items())
        for entry in ordered_entries:
            try:
                shelter_one_start = entry[1]['start_loc']
                shelter_one_dest = entry[1]['dest']
            except KeyError:
                pass
            if shelter_one_start is not None:
                return shelter_one_start
            elif shelter_one_dest is not None:
                return shelter_one_dest
            else:
                print("This hiker's second validated entry has a shelter id equal to the "
                      "first validated entry. Trying next entry.")

    """
    get_second_validated_shelter -Returns the second validated/mapped shelter in the hiker journal.
    @param sorted_journal -The hiker journal read from the validated json file sorted by entry number.
    @return shelter_two -The second validated/mapped shelter in the hiker journal.
    """
    def get_second_validated_shelter(self, sorted_journal):
        ordered_entries = list(sorted_journal.items())
        for entry in ordered_entries:
            try:
                shelter_two_start = entry[1]['start_loc']
                shelter_two_dest = entry[1]['dest']
            except KeyError:
                pass
            if shelter_two_start is not None:
                if shelter_two_start['shelter_id'] != self.shelter_one['shelter_id']:
                    return shelter_two_start
            elif shelter_two_dest is not None:
                if shelter_two_dest['shelter_id'] != self.shelter_one['shelter_id']:
                    return shelter_two_dest
            else:
                print("This hiker's second validated entry has a shelter id equal to the "
                      "first validated entry. Trying next entry.")

    """
    sortHikerJournal -Takes an unsorted hiker trail journal and returns a journal sorted by entry number.
    @param hiker_journal -An unsorted hiker journal dictionary.
    @return sorted_journal -The hiker journal sorted by entry number.
    """
    def sort_hiker_journal(self, hiker_journal):
        sorted_journal = OrderedDict()
        sorted_int_journal = {int(k): v for k, v in hiker_journal.items()}
        for key in sorted(sorted_int_journal.keys()):
            sorted_journal[key] = hiker_journal[str(key)]
        return sorted_journal

    """
    calculate_initial_compass_bearing -Calculates the bearing between two points.
    The formulae used is the following:
        θ = atan2(sin(Δlong).cos(lat2),
                  cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
    :Parameters:
      - `pointA: The tuple representing the latitude/longitude for the
        first point. Latitude and longitude must be in decimal degrees
      - `pointB: The tuple representing the latitude/longitude for the
        second point. Latitude and longitude must be in decimal degrees
    :Returns:
      The bearing in degrees
    :Returns Type:
      float
    @Author: jeromer
    @Source: https://gist.github.com/jeromer/2005586
    """
    def calculate_initial_compass_bearing(self, pointA, pointB):
        if (type(pointA) != tuple) or (type(pointB) != tuple):
            raise TypeError("Only tuples are supported as arguments")
        lat1 = math.radians(pointA[0])
        lat2 = math.radians(pointB[0])
        diffLong = math.radians(pointB[1] - pointA[1])
        x = math.sin(diffLong) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
                * math.cos(lat2) * math.cos(diffLong))
        initial_bearing = math.atan2(x, y)
        # Now we have the initial bearing but math.atan2 return values
        # from -180° to + 180° which is not what we want for a compass bearing
        # The solution is to normalize the initial bearing as shown below
        initial_bearing = math.degrees(initial_bearing)
        compass_bearing = (initial_bearing + 360) % 360
        return compass_bearing

    """
    determine_cardinal_direction -Given a compass bearing, returns the cardinal direction associated with that bearing.
    @param compass_bearing -The initial compass bearing between two validated shelters.
    @return cardinal_dir -The cardinal direction of the compass rose associated with the provided compass bearing.
    """
    def determine_cardinal_direction(self, compass_bearing):
        if compass_bearing >= 0 and compass_bearing < 45:
            return 'North'
        elif compass_bearing >= 45 and compass_bearing < 90:
            return 'Northeast'
        elif compass_bearing >= 90 and compass_bearing < 135:
            return 'East'
        elif compass_bearing >= 135 and compass_bearing < 180:
            return 'Southeast'
        elif compass_bearing >= 180 and compass_bearing < 225:
            return 'South'
        elif compass_bearing >= 225 and compass_bearing < 270:
            return 'Southwest'
        elif compass_bearing >= 270 and compass_bearing < 315:
            return 'West'
        elif compass_bearing >= 315 and compass_bearing < 360:
            return 'Northwest'
        elif compass_bearing == 360:
            return 'North'

def update_hiker(file_pointer, filename, hiker):
    file_pointer.close()
    os.remove(filename)
    with open(filename, 'w') as fp:
        json.dump(hiker, fp)

def main():
    validated_hikers_data_path = "C:/Users/Chris/Documents/GitHub/ATS/Data/Hiker_Data/Validated_Hikers"
    # Retrieve each validated hiker and determine their direction of travel.
    for filename in os.listdir(validated_hikers_data_path):
        fp = open(validated_hikers_data_path + "/" + filename, 'r')
        delete = []
        try:
            hiker = json.load(fp=fp)
        except:
            print("Critical Error: Couldn't read (via json.load) the file at: " + validated_hikers_data_path + "/" + filename)
            # delete.append(validated_hikers_data_path + "/" + filename)
        '''
        fp.close()
        for file in delete:
            os.remove(file)
        '''
        try:
            dir = hiker['dir']
        except KeyError:
            cardinal_interpreter = DirectionRecorder(hiker=hiker)
            if cardinal_interpreter.shelter_one and cardinal_interpreter.shelter_two:
                start_coordinate = (cardinal_interpreter.shelter_one['lat'], cardinal_interpreter.shelter_one['lon'])
                end_coordinate = (cardinal_interpreter.shelter_two['lat'], cardinal_interpreter.shelter_two['lon'])
                compass_bearing = cardinal_interpreter.calculate_initial_compass_bearing(start_coordinate, end_coordinate)
                cardinal_direction = cardinal_interpreter.determine_cardinal_direction(compass_bearing=compass_bearing)
            else:
                print("Two Coordinates are required to determine an "
                      "initial compass bearing. Therefore hiker['dir'] = None")
            if cardinal_direction:
                if "North" in cardinal_direction:
                    hiker['dir'] = "Northbound"
                elif "South" in cardinal_direction:
                    hiker['dir'] = "Southbound"
            else:
                print("Although both coordinates were supplied; the cardinal-direction-interpreter "
                      "failed to retrieve a valid direction. Therefore hiker['dir'] = None")
                hiker['dir'] = "None"
            update_hiker(file_pointer=fp, filename=(validated_hikers_data_path + "/" + filename), hiker=hiker)

if __name__ == '__main__':
    main()
