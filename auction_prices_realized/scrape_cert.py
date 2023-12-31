#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime
import pandas as pd
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

PAGE_MAX = 250
SCRAPE_URL = "https://www.psacard.com/auctionprices/GetItemLots"
EXAMPLE_URL = "https://www.psacard.com/cert/75518283"

class PsaCert:
    def __init__(self, certnum):
        current_directory = os.getcwd()
        print(f"Instantiated in directory: {current_directory}")

        self.certnum = certnum
        self.card_url = f"https://www.psacard.com/cert/{certnum}"
        self.card_image_name = f"cert_{certnum}.jpg"
    
    def get_image(self):
        print(f"{datetime.now().time()}: Getting cert info for {self.certnum}")

        # set up session
        sess = requests.Session()
        sess.mount("https://", requests.adapters.HTTPAdapter(max_retries=5))
        r = sess.get(EXAMPLE_URL)
        r.raise_for_status()
        
        # selenium config
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(options=options)
        driver.get(self.card_url)
        
        try:
            # get element containing the image
            front_image_element = WebDriverWait(driver, 3).until(EC.visibility_of_all_elements_located((By.ID, "certImgFront")))
            
            # get the image URL for both possible sizes
            img_url = front_image_element[0].find_element(By.TAG_NAME, "img").get_attribute('src')
            img_url_large = img_url.replace('/small/', '/large/')
            
            # get large image or small if not available
            try:
                img_data = requests.get(img_url_large).content
                with open(self.card_image_name, 'wb') as f:
                    f.write(img_data)
            except requests.exceptions.RequestException as e:
                print(f"Failed to download 'large' image: {e}")
                try:
                    img_data_small = requests.get(img_url).content
                    with open(self.card_image_name, 'wb') as f:
                        f.write(img_data_small)
                except:
                    print(f"Cert image can't be downloaded?")
        except:
            print('Cert Image Not Available :(')

if __name__ == '__main__':
    # Input validation
    try:
        input_url = [sys.argv[1]]
        if not input_url or not isinstance(input_url, str):
            raise ValueError("input must be a url string with base 'https://www.psacard.com/auctionprices/'")
    except IndexError:
        # If no input url provided, read in urls from urls.txt
        if not os.path.exists("urls.txt"):
            raise ValueError("no input url passed and 'urls.txt' not found")
        with open("urls.txt") as f:
            urls = [n for n in f.read().split("\n") if n]

    # If psa-scrape/data doesn't exist, create it
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Iterate over all urls
    for url in urls:
        # Initialize class and execute web scraping
        pap = PsaCert(url)
        pap.scrape()
