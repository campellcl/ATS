from selenium import webdriver

driver = webdriver.Firefox()
user_dump = open("hikers.txt", 'r')
at_hikers = open("at-hikers.txt", 'w')

def fileLineCount(fname):
    with open(fname) as file:
        for i, l in enumerate(file):
            pass
        return i + 1

num_hikers = fileLineCount("hikers.txt")

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
