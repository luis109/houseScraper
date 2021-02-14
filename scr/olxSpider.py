# IMPORTS
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# For waiting
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

#For CSV
import csv

class olxSpider_driver():
    # Paths
    start_url = ""

    # Wait options
    start_driver_time = 10
    next_page_wait_time = 8

    def __init__(self, start_url, start_time, next_time):
        # Use headless mode
        self.chrome_options = Options()
        # self.chrome_options.add_argument("--headless")
        self.driver_path = '/usr/bin/chromedriver'

        # Selenium driver
        self.driver = webdriver.Chrome(executable_path=self.driver_path, chrome_options=self.chrome_options)

        # Options
        self.start_url = start_url
        self.start_driver_time = start_time
        self.next_page_wait_time = next_time

        # Initialize and set wait
        self.driver.get(start_url)
        self.driver.implicitly_wait(20)
        time.sleep(self.start_driver_time)

        # Set preferences
        self.cookiePreference()

    def __del__(self):
        self.driver.quit()

    def cookiePreference(self):
        self.driver.find_element_by_xpath("//button[@id = 'onetrust-pc-btn-handler']").click()
        time.sleep(1)
        self.driver.find_element_by_xpath("//button[@class = 'save-preference-btn-handler onetrust-close-btn-handler']").click()
        time.sleep(self.start_driver_time/2)

    def nextPage(self):
        try:
            next_arrow_elem = self.driver.find_element_by_xpath("//span[@class = 'fbold next abs large']/a")
            next_arrow_elem.click()
            time.sleep(self.next_page_wait_time)
            return True
        except:
            return False

        # if "disabled" in next_arrow_elem.get_attribute("class"):
        #     return False
        # else:
        #     next_arrow_elem.click()
        #     time.sleep(self.next_page_wait_time)
        #     return True

    def getListingsInPage(self):
        page_listings = self.driver.find_elements_by_xpath("//tr[@class = 'wrap']")
        
        page_links=list()
        for pl in page_listings:
            if pl.get_attribute("rel") == "":
                page_links += [pl.find_element_by_xpath(".//a").get_attribute("href")]
        return page_links

    def getAllListings(self):
        links=list()
        while True:
            links += self.getListingsInPage()
            if not self.nextPage():
                break
        return links

    def parseListing(self, url):
        
        # Fetch listing
        self.driver.get(url)

        # Debug
        print(self.driver.current_url)

        # Auxiliar element parsing
        #   ID and Date
        bottom_bar = self.driver.find_elements_by_xpath("//div[@id = 'offerbottombar']/ul/li//strong")
        listing_id = bottom_bar[2].text
        listing_date = bottom_bar[0].text[3:]

        #   Price  
        try:          
            listing_price = self.driver.find_element_by_xpath("//strong[@class = 'pricelabel__value arranged']").text[:-2].replace(".","")
        except:
            listing_price = self.driver.find_element_by_xpath("//strong[@class = 'pricelabel__value not-arranged']").text[:-2].replace(".","")

        #   Coordinates
        listing_coordinate_elem = self.driver.find_element_by_xpath("//div[@id = 'mapcontainer']")
        listing_lat = listing_coordinate_elem.get_attribute("data-lat")
        listing_lon = listing_coordinate_elem.get_attribute("data-lon")
        listing_coordinates = listing_lat + " " + listing_lon

        #   Details
        listing_details = { "Anunciante": "",
                            "Mobilado": "",
                            "Condição": "",
                            "Área útil": "",
                            "Casas de Banho": "",
                            "Certificado Energético": "",
                            "Tipologia": ""
                            }
        
        listing_details_fields = self.driver.find_elements_by_xpath("//span[@class = 'offer-details__name']")
        listing_details_data = self.driver.find_elements_by_xpath("//strong[@class = 'offer-details__value']")
        
        for i in range(len(listing_details_fields)):
            listing_details[listing_details_fields[i].text] = listing_details_data[i].text

        #   List construction
        listing_values = [  listing_id,                                                             # ID
                            listing_date,                                                           # Date
                            listing_coordinates,                                                    # Coordinates
                            listing_details["Tipologia"][1:],                                       # Rooms
                            listing_details["Casas de Banho"],                                      # WCs
                            listing_details["Área útil"][:-3],                                      # Area Util
                            listing_details["Condição"],                                            # Condição            
                            listing_details["Mobilado"],                                            # Mobilado            
                            listing_details["Certificado Energético"],                              # Eficiencia Energetica
                            listing_details["Anunciante"],                                          # Anunciante
                            listing_price,                                                          # Price
                            self.driver.current_url,                                                # URL
                            self.driver.find_element_by_xpath("//div[@id = 'textContent']").text    # Description
                        ]

        return listing_values

    def parseAllListingsCSV(self, csv_path):

        # Get all listings
        links = self.getAllListings()

        # Setup CSV
        csv_file = open(csv_path + "olx_houses.csv", mode='w')
        csv_writer_handle = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        #   Field names
        field_names = [ 'ID',
                        'Data', 
                        'Coordenadas', 
                        'Quartos', 
                        'WCs',
                        'Area Util (m2)',
                        'Condição', 
                        'Mobilado',
                        'Eficiencia Energetica',
                        'Anunciante',
                        'Preço', 
                        'URL', 
                        'Descrição'
                        ]
        csv_writer_handle.writerow(field_names)

        # Fill CSV
        for l in links:
            csv_writer_handle.writerow(self.parseListing(l))
        csv_file.close()