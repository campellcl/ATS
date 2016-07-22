"""
HikerValidator.py
Handles the mapping between user entered text and GPS coordinates.
@Author: Chris Campell
@Version: 7/22/2016
"""

import os
import json

class HikerValidator(object):
    """
    HikerValidator(object) -Wrapper for ShelterValidator, HostelValidator, and GeoValidator.
    @Author: Chris Campell
    @Version: 7/22/2016
    """

    """
    __init__ -Constructor for objects of type HikerValidator.
    @param -TODO:
    @param -TODO:
    @param -TODO:
    """
    def __init__(self, validated_shelters, validated_hostels, validated_places):
        self.validated_shelters = validated_shelters
        self.validated_hostels = validated_hostels
        self.validated_places = validated_places
        self.storage_location = "C:/Users/Chris/Documents/GitHub/ATS/Data"

    """
    validate_start_loc -
    @return shelter_name -The lookup key for the validated shelter dictionary.
    """
    def validate_start_loc(self, unvalidated_start_loc):
        if unvalidated_start_loc is None:
            return None
        unvalidated_start_loc = str.lower(unvalidated_start_loc)
        # print("Mapping Start Location: %s..." % unvalidated_start_loc)
        for shelter_name, entry in self.validated_shelters.items():
            shelter_name = str.lower(shelter_name)
            # TODO: Fuzzy string comparison.
            if unvalidated_start_loc == shelter_name:
                # print("Success! Start Location: %s Mapped to Lookup Key: %s" % (unvalidated_start_loc, shelter_name))
                return shelter_name
        # print("Failure. Start Location: %s was unable to be mapped to a shelter dictionary lookup key." % unvalidated_start_loc)
        return None

    """
    """
    def validate_dest(self, unvalidated_destination):
        if unvalidated_destination is None:
            return None
        unvalidated_dest = str.lower(unvalidated_destination)
        # print("Mapping Destination Location: %s..." % unvalidated_dest)
        for shelter_name, entry in self.validated_shelters.items():
            shelter_name = str.lower(shelter_name)
            # TODO: Fuzzy string comparison.
            if unvalidated_dest == shelter_name:
                # print("Success! Destination: %s Mapped to Lookup Key: %s" % (unvalidated_dest, shelter_name))
                return shelter_name
        # print("Failure. Destination: %s was unable to be mapped to a shelter dictionary lookup key." % unvalidated_dest)
        return None

    """
    """
    def validate_entry(self, entry):
        start_loc_lookup_key = self.validate_start_loc(entry['start_loc'])
        dest_lookup_key = self.validate_dest(entry['dest'])
        if start_loc_lookup_key is not None:
            entry['start_loc'] = {
                'shelter_name': start_loc_lookup_key,
                'shelter_id': self.validated_shelters[start_loc_lookup_key]['id'],
                'lat': self.validated_shelters[start_loc_lookup_key]['lat'],
                'lon': self.validated_shelters[start_loc_lookup_key]['lon'],
                'type': self.validated_shelters[start_loc_lookup_key]['type']
            }
        else:
            entry['start_loc'] = None
        if dest_lookup_key is not None:
            entry['dest'] = {
                'shelter_name': dest_lookup_key,
                'shelter_id': self.validated_shelters[dest_lookup_key]['id'],
                'lat': self.validated_shelters[dest_lookup_key]['lat'],
                'lon': self.validated_shelters[dest_lookup_key]['lon'],
                'type': self.validated_shelters[dest_lookup_key]['type']
            }
        else:
            entry['dest'] = None
        return entry

    """
    validate_shelters -Goes through the hiker's journal geocoding each starting location and destination.
    @param hiker -The deserialized hiker object read from the json file.
    """
    def validate_shelters(self, hiker):
        unmapped_entries = []
        unvalidated_journal = hiker['journal']
        for entry_num, entry in unvalidated_journal.items():
            geocoded_entry = self.validate_entry(entry)
            if geocoded_entry['start_loc'] is None and geocoded_entry['dest'] is None:
                unmapped_entries.append(entry_num)
            else:
                hiker[entry_num] = geocoded_entry
        num_mapped = len(unvalidated_journal) - len(unmapped_entries)
        print("Hiker %s (%s)'s Geocoding Statistics: There were %d entries successfully mapped out of %d." %(hiker['identifier'], hiker['name'], num_mapped, len(unvalidated_journal)))
        for unmapped_entry in unmapped_entries:
            del hiker['journal'][unmapped_entry]

    """
    write_validated_hiker -Writes a geocoded hiker to Hiker_Data/Validated_Hikers in json format.
    @param hiker -The deserialized hiker object read from the json file.
    """
    def write_validated_hiker(self, hiker):
        validated_hikers_data_path = "C:/Users/Chris/Documents/GitHub/ATS/Data/Hiker_Data/Validated_Hikers"
        hiker_id = hiker['identifier']
        with open(validated_hikers_data_path + "/" + str(hiker_id) + ".json", 'w') as fp:
            json.dump(hiker, fp=fp)


"""
get_validated_shelters -Returns a dictionary of the shelters validated using the combined TNL and ATC data sets.
@param validated_shelters_path -The path to the CSV file containing the validated shelters.
@return validated_shelters -A dictionary containing the geocoded shelters.
"""
def get_validated_shelters(validated_shelters_path):
    validated_shelters = {}
    line_num = 0
    with open(validated_shelters_path, 'r') as fp:
        for line in iter(fp):
            if not line_num == 0:
                split_string = str.split(line, sep=",")
                shelter_name = split_string[0]
                shelter_id = split_string[1]
                data_set = split_string[2]
                lat = float(split_string[3])
                lon = float(split_string[4])
                type = split_string[5]
                validated_shelters[str.lower(shelter_name)] = {
                    'id': shelter_id, 'num': 0, 'dataset': data_set,
                    'type': type, 'lat': lat, 'lon': lon
                }
            line_num += 1
    return validated_shelters

"""
"""
def get_validated_hostels(validated_hostels_path):
    pass

"""
"""
def get_validated_places(validated_places_path):
    pass

def main():
    unvalidated_hikers_data_path = "C:/Users/Chris/Documents/GitHub/ATS/Data/Hiker_Data"
    validated_hikers_data_path = "C:/Users/Chris/Documents/GitHub/ATS/Data/Hiker_Data/Validated_Hikers"
    validated_data_path = "C:/Users/Chris/Documents/GitHub/ATS/Data/Shelter_Data"

    # Go through the list of unvalidated hikers and validate.
    for filename in os.listdir(unvalidated_hikers_data_path):
        if filename not in os.listdir(validated_hikers_data_path):
            with open(unvalidated_hikers_data_path + "/" + filename, 'r') as fp:
                hiker = json.load(fp=fp)
            validated_shelters = get_validated_shelters(validated_shelters_path=validated_data_path + "/validated_shelters.csv")
            validated_hostels = get_validated_hostels(validated_hostels_path=validated_data_path + "/validated_hostels.csv")
            validated_places = get_validated_places(validated_places_path=validated_data_path + "/validated_places.csv")
            validator = HikerValidator(validated_shelters=validated_shelters,
                                       validated_hostels=validated_hostels, validated_places=validated_places)
            validator.validate_shelters(hiker)
            if len(hiker['journal']) > 0:
                validator.write_validated_hiker(hiker)
        else:
            print("Hiker %s Has Already ben Validated." % filename)

if __name__ == '__main__':
    main()