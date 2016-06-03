"""
ShapeFileParser.py
Parses an ESRI ShapeFile and stores the data using numpy.
@Author: Chris Campell
@Version: 5/27/2016
"""
import sys
from selenium import webdriver

num_hikers = 0
hikers = []

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
def main(args):
    num_hikers = 0
    driver = webdriver.Firefox()
    # start_url = "http://www.trailjournals.com/journal_index.cfm?year=&trail=Appalachian+Trail&gotrail=+Go+"
    start_url = "http://www.trailjournals.com/journals/appalachian_trail/"
    driver.get(start_url)

    user_table_xpath = \
        "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/div[2]/table/tbody/tr/td[1]/table/tbody"
    hiker_divs_xpath = user_table_xpath + "//tr//td[position()=2]/div"
    hiker_div_xpath = user_table_xpath + "/tr/td[position()=2]/div"
    hiker_divs = driver.find_elements_by_xpath(hiker_divs_xpath)
    next_hyperlink_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/div[2]/div[1]/a[2]"
    # slect table's children as to parse for <b></b> trail name or no trail name.
    # hiker_tr_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/div[2]/table/tbody/tr/td[1]/table/tbody/child::*"
    hiker_tr_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/div[2]/table/tbody/tr/td[1]/table/tbody/child::*"
    hiker_trs = driver.find_elements_by_xpath(hiker_tr_xpath)
    num_trs_on_page = len(hiker_trs)


    for div in hiker_divs:
        child_xpath_one = hiker_tr_xpath + "//child"
        child_xpath_two = hiker_div_xpath + "/ancestor::*"
        hiker_trail_name = ""
        hiker_div_content = hiker_divs[num_hikers]
        hiker_info_string = hiker_div_content.text

        # TODO: Only hikers with trail names are included in the xpath somehow. Resolve this.
        try:
            hiker_information = driver.find_elements_by_xpath(child_xpath_two)
            hiker_trail_name = driver.find_elements_by_xpath(child_xpath_one)
            hiker_tn = hiker_trail_name[0]
            # hiker_trail_name = hiker_trail_names[num_hikers].text
        except ValueError:
            # hiker trail name not provided
            pass
        hiker = getHikerInfo(hiker_trail_name, hiker_info_string)
        hikers.append(hiker)
        num_hikers += 1
        '''
        try:
            hiker_trail_name = driver.find_elements_by_xpath(hiker_div_xpath + "/b")
            hiker_has_trail_name = True
            # TODO: how to use xpath to get text between two <br> elements with no id or class tag.
        except ValueError:
            # hiker has no trail name.
            pass
        hiker_info_string = hiker_names[num_hikers].text
        hiker_name = hiker_info_string.split("\n")[1]
        hikers.append({'trail_name' : hiker_trail_names[num_hikers].text, 'name' : hiker_name})
        num_hikers += 1
        '''

    '''
    user_table_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/table[2]/tbody"
    # hiker_divs_xpath = user_table_xpath + "//tr[@bgcolor!=Silver]"
    hiker_divs_xpath = user_table_xpath + "//tr//td"
    hiker_trail_names_xpath = hiker_divs_xpath + "/b"
    hiker_names_xpath = hiker_divs_xpath
    hiker_divs = driver.find_elements_by_xpath(user_table_xpath)
    hiker_trail_names = driver.find_elements_by_xpath(hiker_trail_names_xpath)
    hiker_names = driver.find_elements_by_xpath(hiker_names_xpath)
    for div in hiker_divs:
        hikers.append({'trail_name' : hiker_trail_names[num_hikers].text, 'name' : hiker_names[num_hikers].text, 'direction' : 'Northbound/Southbound/NA'})
        num_hikers += 1
    '''

if __name__ == '__main__':
    main(sys.argv)
    print(hikers)