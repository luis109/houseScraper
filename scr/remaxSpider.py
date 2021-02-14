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

class remaxSpider_driver():
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
        self.driver.implicitly_wait(60)
        time.sleep(self.start_driver_time)

    def __del__(self):
        self.driver.quit()

    def nextPage(self):
        # next_arrow_elem = WebDriverWait(self.driver, 30).until(
        #                     EC.presence_of_element_located(
        #                         (By.XPATH, "//div[@class = 'pagination-component']/ul/li[7]")
        #                         )
        #                     )

        next_arrow_elem = self.driver.find_element_by_xpath("//div[@class = 'pagination-component']/ul/li[7]")

        if "disabled" in next_arrow_elem.get_attribute("class"):
            return False
        else:
            next_arrow_elem.click()
            time.sleep(self.next_page_wait_time)
            return True

    def getListingsInPage(self):
        # page_listings = WebDriverWait(self.driver, 30).until(
        #                     EC.presence_of_all_elements_located(
        #                         (By.XPATH, "//div[@class = 'row results-list ']/div/div/a")
        #                         )
        #                     )

        page_listings = self.driver.find_elements_by_xpath("//div[@class = 'row results-list ']/div/div/a")
        return [pl.get_attribute("href") for pl in page_listings]

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
        #   ID
        try:
            listing_id = self.driver.find_element_by_xpath("//div[@class = 'listing-top-info']/span").text[4:]
        except:
            listing_id = self.driver.find_element_by_xpath("//div[@class = 'listing-top-info']/div").text[4:]

        #   Price
        listing_price = self.driver.find_element_by_xpath("//div[@class = 'listing-top-info']/h2").text[:-2].replace(" ", "")

        #   Coordinates
        try:
            coordinate_elem = self.driver.find_element_by_id("listing-coordinates")
            self.driver.execute_script("arguments[0].style.display = 'block';", coordinate_elem)
            coordinates = coordinate_elem.text.replace(";", " ")
        except:
            coordinates = ""

        #   Details
        details = self.driver.find_elements_by_xpath("//div[@id = 'details']/table/tbody/tr/td")

        # List construction
        listing_values = [  listing_id,                                                             # ID
                            coordinates,                                                            # Coordinates
                            details[9].text,                                                        # Rooms
                            details[11].text,                                                       # WCs
                            details[1].text,                                                        # Area Bruta
                            details[3].text,                                                        # Area Util
                            details[5].text,                                                        # Total do Lote
                            details[7].text,                                                        # Ano de construção
                            details[13].text,                                                       # Piso
                            details[17].text,                                                       # Elevador
                            details[15].text,                                                       # Estacionamento
                            details[19].text,                                                       # Eficiencia Energetica
                            listing_price,                                                          # Price
                            self.driver.current_url,                                                # URL
                            self.driver.find_element_by_xpath("//div[@id = 'description']").text    # Description
                        ]

        return listing_values

    def parseAllListingsCSV(self, csv_path):

        # Get all listings
        links = self.getAllListings()

        # Setup CSV
        csv_file = open(csv_path + "remax_houses.csv", mode='w')
        csv_writer_handle = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        #   Field names
        field_names = [ 'ID', 
                        'Coordenadas', 
                        'Quartos', 
                        'WCs', 
                        'Area Bruta (m2)', 
                        'Area Util (m2)', 
                        'Total do Lote (m2)', 
                        'Ano de Construção', 
                        'Piso', 
                        'Elevador', 
                        'Estacionamento', 
                        'Eficiencia Energetica', 
                        'Preço', 
                        'URL', 
                        'Descrição'
                        ]
        csv_writer_handle.writerow(field_names)

        # Fill CSV
        for l in links:
            csv_writer_handle.writerow(self.parseListing(l))
        csv_file.close()