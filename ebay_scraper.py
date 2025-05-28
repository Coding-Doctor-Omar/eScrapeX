from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from art import logo
import pandas as pd
import time
import re
import os
import sys

urls = {
    "phones": "https://www.ebay.com/b/Cell-Phones-Smartphones/9355/bn_320094",
    "tablets": "https://www.ebay.com/b/Tablets-eReaders/171485/bn_320042",
    "laptops": "https://www.ebay.com/b/Laptops-Netbooks/175672/bn_1648276",
}

csv_names = {
    "phones": "ebay_smartphones.csv",
    "tablets": "ebay_tablets.csv",
    "laptops": "ebay_laptops.csv",
}

def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


class eBayScraper:
    def __init__(self):
        self.products = []
        self.data = {}
        self.current_page_failed = False

    def show_scrape_status(self, state, product_count=0.0, speed=0.0):
        progress = round(product_count / 10020 * 100)
        clear_screen()

        if state == "scraping":
            print(logo)
            print(f"Scraping @{speed} products/s...\n")
            print(f"Scraped a total of {product_count}/10020 products. [{progress}% COMPLETE]")
        elif state == "finished_scraping":
            print(logo)
            print("Scraping finished. Generating CSV file.")
        elif state == "finished_csv":
            print(logo)
            input("CSV created successfully. Press ENTER to go back to main menu.")
        elif state == "next_page":
            print(logo)
            print("GOING TO THE NEXT LISTINGS PAGE...\n")
            print(f"Scraped a total of {product_count}/10020 products. [{progress}% COMPLETE]")
        elif state == "page_failed":
            print(logo)
            print("Possible CAPTCHA detected. All scrapings of this page will be discarded. Attempting to retry page...\n")
            print(f"Scraped a total of {product_count}/10020 products. [{progress}% COMPLETE]")
        else:
            raise ValueError(f"Invalid state argument. Expected 'scraping', 'finished_scraping', 'finished_csv', 'next_page', or 'page_failed' but got '{state}' instead.")


    def scrape_products(self, category):
        if category not in urls:
            raise ValueError("Invalid category argument. Current supported arguments are 'phones', 'tablets', and 'laptops'.")

        url = urls[category]

        # Set up options
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

        # Go to page and prepare
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url=url)
        driver.execute_script("document.body.style.zoom='25%'")

        # Final preparation phase
        current_page = 1

        # Begin (you can change the first while loop to a 'for _ in range(1)' if you want to undergo quick testing).
        while True:
            # We assume the page is working fine by default
            self.current_page_failed = False

            # List of products in this page only
            page_products = []

            # Get current page url
            current_url = driver.current_url

            # Capture Item Cards of the Page
            retries = 0
            while True:

                try:
                    products_section = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "ul.brwrvr__item-results--list"))
                    )
                except TimeoutException:
                    retries += 1
                    if retries > 3:
                        products_section = None
                        break
                    else:
                        driver.refresh()
                else:
                    break

            if products_section:
                page_product_cards = products_section.find_elements(By.CSS_SELECTOR,
                                                                    value=".brwrvr__item-card__wrapper")
            else:
                break

            # Loop Through Each Product in the Page
            for product_card in page_product_cards:
                # Mark the time
                start_time = time.time()

                # Scroll down
                driver.execute_script("window.scrollBy(0, 100);")

                # Get product title, category, and brand
                try:
                    title = product_card.find_element(By.CSS_SELECTOR, value=".bsig__title__text").text.strip()
                except NoSuchElementException:
                    self.current_page_failed = True
                    break

                title = re.sub(r'[^\x00-\x7F]+', '', title)

                try:
                    product_category = driver.find_element(By.CSS_SELECTOR, value="h1.page-title").text.strip()
                except NoSuchElementException:
                    self.current_page_failed = True
                    break

                try:
                    brand_area = product_card.find_element(By.CSS_SELECTOR,
                                                           value=".bsig--subheader").text
                except NoSuchElementException:
                    self.current_page_failed = True
                    break

                if " · " in brand_area:
                    brand = brand_area.split(" · ")[1].strip()
                else:
                    if " " in brand_area or "-" in brand_area or "New" in brand_area or "Used" in brand_area:
                        brand = "Unbranded"
                    else:
                        brand = brand_area.strip()

                # Get product min and max prices
                try:
                    price_text = product_card.find_element(By.CSS_SELECTOR,
                                                           value="span.bsig__price--displayprice").text.strip()
                except NoSuchElementException:
                    self.current_page_failed = True
                    break

                if "to" in price_text:
                    min_price = float(price_text.split("to")[0].strip().replace("$", "").replace(",", ""))
                    max_price = float(price_text.split("to")[1].strip().replace("$", "").replace(",", ""))
                else:
                    min_price = float(price_text.strip().split("$")[1].replace(",", ""))
                    max_price = min_price

                # Get product link
                try:
                    product_link = product_card.find_element(By.CSS_SELECTOR, value=".bsig__title a").get_attribute("href")
                except NoSuchElementException:
                    self.current_page_failed = True
                    break

                # Get product image links
                try:
                    image_elements = product_card.find_elements(By.CSS_SELECTOR, value="img.brwrvr__item-card__image")
                except NoSuchElementException:
                    self.current_page_failed = True
                    break

                image_links = [element.get_attribute("data-originalsrc") for element in image_elements]
                image_links = " ".join(image_links)

                # Add product to the products list
                page_products.append(
                    {
                        "title": title,
                        "category": product_category,
                        "brand": brand,
                        "min_price": min_price,
                        "max_price": max_price,
                        "product_link": product_link,
                        "image_links": image_links,
                    }
                )

                # Calculate and display scraping speed
                elapsed_time = time.time() - start_time
                speed = round(1 / elapsed_time, 2)
                self.show_scrape_status(product_count=len(self.products) + len(page_products), speed=speed, state="scraping")

            # Add page products list to full products list
            if self.current_page_failed:
                self.show_scrape_status(state="page_failed")
                time.sleep(5)
                driver.get(current_url)
                continue
            else:
                for product in page_products:
                    self.products.append(product)

            # Periodically restart the webdriver
            current_page += 1
            if current_page % 30 == 0:
                driver.quit()
                driver = webdriver.Chrome(options=chrome_options)
                driver.get(current_url)
                driver.execute_script("window.scrollBy(0, 1000);")


            # Go to the next page
            self.show_scrape_status(product_count=len(self.products), state="next_page")
            next_page_button = driver.find_element(By.CSS_SELECTOR, value="a[type='next']")
            driver.get(url=next_page_button.get_attribute("href"))
            driver.execute_script("document.body.style.zoom='25%'")
                
        self.show_scrape_status(state="finished_scraping")

        self.data = {
            "title": [product["title"] for product in self.products],
            "category": [product["category"] for product in self.products],
            "brand": [product["brand"] for product in self.products],
            "min_price": [product["min_price"] for product in self.products],
            "max_price": [product["max_price"] for product in self.products],
            "product_link": [product["product_link"] for product in self.products],
            "image_links": [product["image_links"] for product in self.products],
        }

        csv_name = csv_names[category]

        df = pd.DataFrame(self.data).drop_duplicates()
        df.to_csv(f"scrapings/{csv_name}", index=False)
        driver.quit()

        self.show_scrape_status(state="finished_csv")


                







