# IMPORTS
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# For waiting
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time

# Use headless mode
chrome_options = Options()
# chrome_options.add_argument("--headless")

# Use chrome driver
# Driver in use: '/usr/bin/chromedriver'
# driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver', chrome_options=chrome_options)

class remaxSpider():
    start_url = "https://www.remax.pt/comprar?searchQueryState={\"regionName\":\"Paranhos\",\"businessType\":1,\"listingClass\":1,\"page\":1,\"regionID\":\"139772\",\"regionType\":\"Region3ID\",\"sort\":{\"fieldToSort\":\"ContractDate\",\"order\":1},\"mapIsOpen\":false,\"regionCoordinates\":{\"latitude\":41.1603642610245,\"longitude\":-8.619519668643346},\"regionZoom\":12,\"prn\":\"Paranhos,%20Porto\"}"
    driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver', chrome_options=chrome_options)
    start_driver_time = 10
    next_page_wait_time = 3

    def __init__(self):
        self.driver.get(self.start_url)
        time.sleep(self.start_driver_time)

    def __del__(self):
        self.driver.quit()

    def nextPage(self):
        next_arrow_elem = self.driver.find_element_by_xpath("//div[@class = 'pagination-component']/ul/li[7]")
        if "disabled" in next_arrow_elem.get_attribute("class"):
            return False
        else:
            next_arrow_elem.click()
            time.sleep(self.next_page_wait_time)
            return True

    def getListingsInPage(self):
        page_listings = self.driver.find_elements_by_xpath("//div[@class = 'row results-list ']/div/div/a")
        return [pl.get_attribute("href") for pl in page_listings]

    def getAllListings(self):
        links=list()
        while True:
            links += rs.getListingsInPage()
            if not rs.nextPage():
                break
        return links

rs = remaxSpider()
links = rs.getAllListings()

# [print(l) for l in links]
for l in links:
    rs.driver.get(l)
    time.sleep(rs.next_page_wait_time)
del rs

