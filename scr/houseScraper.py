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

# Use headless mode
chrome_options = Options()
# chrome_options.add_argument("--headless")
driver_path = '/usr/bin/chromedriver'
csv_folder_path = "/home/luis/scraper/houseScraper/generated_files/"

class remaxSpider():
    # Paths
    start_url = "https://www.remax.pt/comprar?searchQueryState={\"regionName\":\"Paranhos\",\"businessType\":1,\"listingClass\":1,\"page\":1,\"regionID\":\"139772\",\"regionType\":\"Region3ID\",\"sort\":{\"fieldToSort\":\"ContractDate\",\"order\":1},\"mapIsOpen\":false,\"regionCoordinates\":{\"latitude\":41.1603642610245,\"longitude\":-8.619519668643346},\"regionZoom\":12,\"prn\":\"Paranhos,%20Porto\"}"

    # Wait options
    start_driver_time = 10
    next_page_wait_time = 8

    # Selenium driver
    driver = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)

    def __init__(self):
        self.driver.get(self.start_url)
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
        # time.sleep(self.next_page_wait_time)
        print(url)

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

    def parseAllListingsCSV(self):

        # Get all listings
        links = self.getAllListings()

        # Setup CSV
        csv_file = open(csv_folder_path + "remax_houses.csv", mode='w')
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
        

rs = remaxSpider()
rs.parseAllListingsCSV()
del rs