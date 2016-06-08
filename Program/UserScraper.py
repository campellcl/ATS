import sys
from selenium import webdriver

driver = webdriver.Firefox()
num_hikers = 0
hikers = set([])
#estimated num_hikers = 30,000
estimated_user_bound = 30000
user_dump = open('at-hikers.txt', 'a')

start_url = "http://www.trailjournals.com/entry.cfm?trailname="
journal_name_xpath = "/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/div/font"
# previous = 13347
previous = 20207

print("Bot Active. Archiving users [%d:%d]" %(previous, estimated_user_bound))
for i in range(previous, estimated_user_bound):
    user_url = start_url + str(i)
    driver.get(user_url)
    try:
        not_found = driver.find_element_by_xpath("/html/body/table/tbody/tr[4]/td/table/tbody/tr/td[2]/div[1]")

        if ("The requested" in not_found.text):
            # user invalid.
            pass
        elif ("Appalachian Trail" not in driver.find_element_by_xpath(journal_name_xpath).text):
            # not an Appalachian Trail entry.
            print("User %d is not an AT hiker." % i)
            pass
        else:
            # User is a valid user and their journal is of the AT.
            user_dump.write(str(i) + "\n")
    except:
        pass
user_dump.close()

