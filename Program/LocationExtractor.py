"""
LocationExtractor.py
Extracts and stores relevant AT_Centerline information from the provided KML file.
@Author: Chris Campell
@Date: 6/24/2016
"""
import sys
from lxml import etree
from pykml import parser
from csv import writer

"""
LocationExtractor -Extracts necessary AT Centerline information from the provided KML file.
"""
class LocationExtractor(object):

    """
    __init__ -Default constructor for objects of type LocationExtractor.
    @param kml_file_name -The name of the kml file from which to extract coordinates.
    @param output_file_name -The name of the file from which to write the extracted coordinates.
    """
    def __init__(self,kml_file_name=None,output_file_name=None):
        self.kml_file_name = kml_file_name
        self.output_file_name = output_file_name
        self.coordinates = []

    """
    openKML -Opens and parses the KML file specified in the class constructor.
    """
    def openKML(self):
        with open(self.kml_file_name) as fp:
            self.kml_doc = parser.parse(fp)
            root = parser.fromstring(open(self.kml_file_name, 'r').read())
            # print(self.kml_root.Document.name)
            self.placemarks = root.Document.Folder.getchildren()
            # print(root.Document.Folder.getchildren())
            # print(root.Document.Folder.Placemark.LineString.coordinates)

    """
    extractCenterline -Parses the KML object, removing all coordinates for the AT centerline.
    """
    def extractCenterline(self):
        i = 0
        # Go through every child element read by the lxml pyKML parser and extract <LineString> coordinates.
        for childElement in self.placemarks:
            if i > 1:
                coords = str.split(childElement.LineString.coordinates.text, sep=' ')
                j = 0
                for coord in coords:
                    if j == 0:
                        coords[0] = str.strip(coord, '\n\t\t\t\t\t')
                        xyz = str.split(coords[0], sep=',')
                        coords[0] = {'lon': xyz[0], 'lat': xyz[1], 'alt': xyz[2]}
                    elif j == len(coords) - 1:
                        del coords[len(coords) - 1]
                    else:
                        xyz = str.split(coords[j], sep=',')
                        coords[j] = {'lon': xyz[0], 'lat': xyz[1], 'alt': xyz[2]}
                    j += 1
                self.coordinates.append(coords)
            i += 1


    """
    writeCenterline -Writes the extracted KML <LineString> coordinates to the
        csv file specified in the LocationExtractor constructor.
    """
    def writeCenterline(self):
        with open(str(self.output_file_name), 'w') as fp:
            fp.write("lon,lat,alt\n")
            for coordinateList in self.coordinates:
                for coordinate in coordinateList:
                    fp.write(coordinate['lon'] + "," + coordinate['lat'] + "," + coordinate['alt'] + "\n")
"""
main -Default main method for LocationExtractor.py
@param cmd_args -Default command line arguments.
"""
def main(cmd_args):
    kml_file_name = "C:/Users/Chris/Documents/GitHub/ATS/Data/AT_Conservancy_Data/AT_Centerline_12-23-2014/doc.kml"
    extractor = LocationExtractor(kml_file_name=kml_file_name, output_file_name="AT_Centerline.csv")
    print("Location Extractor: Now parsing KML file.")
    extractor.openKML()
    print("Location Extractor: Extracting GIS Coordinates from file.")
    extractor.extractCenterline()
    print("Location Extractor: Writing extracted GIS Coordinates to specified CSV file.")
    extractor.writeCenterline()

if __name__ == '__main__':
    main(sys.argv)
