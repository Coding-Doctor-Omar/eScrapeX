from art import logo, menu_options, categories_options
from ebay_scraper import eBayScraper
import os
import sys


def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def load_main_menu():
    clear_screen()
    print(logo)
    print(menu_options)
    print("\n")
    return input("Choose an option: ").lower()

def load_categories_screen():
    clear_screen()
    print(categories_options)
    print("\n")
    return input("Choose a product category: ").lower()

def scrape_products(category):
    scraper = eBayScraper()
    scraper.scrape_products(category=category)

def load_about_screen():
    clear_screen()
    print("What is eScrapeX?\n")
    print("eScrapeX is an experimental tool made for testing purposes.\n")
    print("It scrapes product data from all product listings (with effective pagination handling) from eBay.com based on product category and packs the results into a csv file.\n")
    print("The file lies inside a subdirectory called 'scrapings'. Look for it in the same directory of 'main.py'.\n")
    print("Scraped data includes product titles, product links, all image links per product, product prices, and product brands.\n")
    print("The scraper has an automatic deduplication capability, so the resulting dataset will not have duplicates.\n")
    print("Full product duplicates are the only ones removed, but subset duplicates are kept.\n")
    print("This scraper may violate eBay's terms of service, so use AT YOUR OWN RISK.\n")
    print("I am not affiliated in any way with eBay.\n\n")
    print(f"My GitHub Profile: https://github.com/Coding-Doctor-Omar")
    print(f"Support Me Here: https://www.paypal.me/codingdromar\n\n")
    input("Press ENTER to go back to Main Menu.")


def main():
    while True:
        menu_response = load_main_menu()

        if menu_response not in ["1", "2", "3"]:
            input("Invalid option. Press ENTER to retry.")
        elif menu_response == "1":
            category_response = load_categories_screen()
            if category_response not in ["1", "2", "3", "4"]:
                input("Invalid category choice. You will be redirected to the main menu. Press ENTER to retry.")
            elif category_response == "1":
                clear_screen()
                print("Initializing...")
                scrape_products(category="phones")
            elif category_response == "2":
                clear_screen()
                print("Initializing...")
                scrape_products(category="tablets")
            elif category_response == "3":
                clear_screen()
                print("Initializing...")
                scrape_products(category="laptops")
            else:
                pass
        elif menu_response == "2":
            load_about_screen()
        else:
            sys.exit(0)


if __name__ == "__main__":
    main()
