"""
ShelterCombinator.py
Combines the AT Shelter data provided by the AT Conservancy with the data provided by TN Landforms
@Author: Chris Campell
@Version: 7/11/2016
"""
import sys

class ShelterCombinator(object):

    def __init__(self):
        self.num_ATC = 0
        self.ATCS = {}
        self.num_TNLS = 0
        self.TNLS = {}
        self.shelters = {}

    """
    parseATCData -Parses all necessary shelter data from the Appalachian Trail Conservancy (ATC) files.
    """
    def parseATCData(self):
        print("SHELTER COMBINATOR: Parsing Appalachian Trail Conservancy (ATC) Data...")
        fp = open("C:/Users/Chris/Documents/GitHub/ATS/Data/AT_Conservancy_Data/AT_Shelters/AT_Shelters.csv", 'r')
        line_num = 0
        for line in iter(fp):
            if line_num == 0:
                pass
            else:
                entry = line.split(sep=",")
                name = entry[1]
                type = entry[2]
                lat = entry[4]
                lon = entry[5]
                self.ATCS[str(name)] = {'data_set': 'ATC', 'type': str(type), 'lat': lat, 'lon': lon}
            line_num += 1
        fp.close()
        self.num_ATC = len(self.ATCS)
        print("SHELTER COMBINATOR: Parsing Finished. There are %d shelters in the ATC Data Set." % self.num_ATC)


    """
    parseTNLData -Parses all necessary shelter data from the Tennessee Landforms files.
    """
    def parseTNLData(self):
        print("SHELTER COMBINATOR: Parsing Tennessee Landform (TNL) Data...")
        fp = open("C:/Users/Chris/Documents/GitHub/ATS/Data/TN_Landforms_Data/AT_Shelters/AT_Shelters2.csv", 'r')
        line_num = 0
        for line in iter(fp):
            if line_num == 0:
                pass
            else:
                entry = line.split(sep="\"")
                name = entry[6]
                name = name.replace(",", "")
                if "Shelter" in name:
                    type = "Shelter"
                elif "Lean-to" in name:
                    type = "Lean-to"
                elif "Hut" in name:
                    type = "Hut"
                else:
                    type = "Unknown"
                coords = entry[len(entry) - 2]
                coords = coords[20:len(coords)]
                coords_end = coords.find("</coordinates>")
                coords = coords[0:coords_end]
                coords = coords.split(sep=",")
                lat = coords[1]
                lon = coords[0]
                self.TNLS[str(name)] = {'data_set': 'TNL', 'type': type, 'lat': lat, 'lon': lon}
            line_num += 1
        fp.close()
        self.num_TNLS = len(self.TNLS)
        print("SHELTER COMBINATOR: Parsing Finished. There are %d shelters in the TNL Data Set." % self.num_TNLS)

    """
    combineData -Combines data from the ATC and TNL files into one data set.
    """
    def combineData(self):
        for key, value in self.ATCS.items():
            self.shelters[key] = value
        for key, value in self.TNLS.items():
            self.shelters[key] = value

    """
    writeData -Writes the combined data to a single Google Fusion Table styled CSV file.
    """
    def writeData(self):
        print("SHELTER COMBINATOR: Writing Combined Shelter Data...")
        fp = open("my_at_shelters.csv", 'w')
        i = 0
        for key, value in self.shelters.items():
            if i == 0:
                fp.write("shelter,data_set,lat,lon,type\n")
            else:
                fp.write("%s,%s,%f,%f,%s\n" %(key, value['data_set'], float(value['lat']),
                                              float(value['lon']), value['type']))
            i += 1
        fp.close()
        print("SHELTER COMBINATOR: Data Written. There are %d shelters in the combined data set ("
              "duplicates discarded)." % len(self.shelters))

def main(cmd_args):
    combiner = ShelterCombinator()
    combiner.parseATCData()
    combiner.parseTNLData()
    combiner.combineData()
    combiner.writeData()

if __name__ == '__main__':
    main(sys.argv)
