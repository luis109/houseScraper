# IMPORTS
from remaxSpider import remaxSpider_driver
from olxSpider import olxSpider_driver

# General
csv_folder_path = "/home/luis/scraper/houseScraper/generated_files/"
start_wait_time = 10
next_wait_time = 8

# # Remax
# start_url = "https://www.remax.pt/comprar?searchQueryState={%22regionName%22:%22Paranhos%22,%22businessType%22:1,%22listingClass%22:1,%22page%22:1,%22regionID%22:%22139772%22,%22regionType%22:%22Region3ID%22,%22sort%22:{%22fieldToSort%22:%22ContractDate%22,%22order%22:1},%22mapIsOpen%22:false,%22regionCoordinates%22:{%22latitude%22:41.1603642610245,%22longitude%22:-8.619519668643346},%22regionZoom%22:12,%22prn%22:%22Paranhos,%20Porto%22}"
# rs = remaxSpider_driver(start_url, start_wait_time, next_wait_time)
# rs.parseAllListingsCSV(csv_folder_path)
# del rs

    # Wait options
    start_driver_time = 10
    next_page_wait_time = 8

    # Selenium driver