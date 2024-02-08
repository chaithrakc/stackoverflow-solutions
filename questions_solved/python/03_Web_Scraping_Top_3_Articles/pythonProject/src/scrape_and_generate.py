from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def initialize_webdriver(headless=False):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    driver = webdriver.Chrome('../chromedriver-win64/chromedriver.exe', options=chrome_options)
    return driver


if __name__ == '__main__':
    chrome_driver = initialize_webdriver(headless=True)

    urls = [
        'https://www.businesswire.com/portal/site/home/search/?searchType=all&searchTerm=lobe%20sciences&searchPage=1',
        'https://www.businesswire.com/portal/site/home/search/?searchType=all&searchTerm=enveric&searchPage=1',
        'https://www.businesswire.com/portal/site/home/search/?searchType=all&searchTerm=cybin&searchPage=1',
        'https://www.businesswire.com/portal/site/home/search/?searchType=all&searchTerm=delix&searchPage=1']

    try:
        for url in urls:
            # loading the webpage
            chrome_driver.get(url)

            # wait for the list of items to load
            WebDriverWait(chrome_driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//ul[@class='bw-news-list']")))

            # scraping top 3 sites
            list_item = chrome_driver.find_element(By.XPATH, "//ul[@class='bw-news-list']")
            top_sites = list_item.find_elements(By.XPATH, "//li/h3/a")
            for index, item in enumerate(top_sites[:3], 0):
                print(f'Title {index}: {item.text}')
                print(f"URL {index}: {item.get_attribute('href')}")
            print('---------------------------------------------------')

    finally:
        chrome_driver.quit()
