import time
import logging
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def sanitize_car_model(car_model):
    # Replace spaces with hyphens and remove anything after '('
    return car_model.split(' (')[0].replace(' ', '-')

def generate_url(car_make, car_model, generation=None):
    base_url = "https://www.otomoto.pl/osobowe"
    car_make_formatted = car_make.lower().replace(" ", "-").replace("&", "and")
    car_model_formatted = car_model.lower().replace(" ", "-").split(" (")[0]

    if car_make_formatted == "mercedes-benz":
        if car_model_formatted.startswith("klasa"):
            car_model_parts = car_model_formatted.split("-")
            car_model_formatted = f"{car_model_parts[1]}-{car_model_parts[0]}"
        elif car_model_formatted in ['cla', 'clk', 'cls', 'gl', 'gla', 'glb', 'glc', 'gle', 'glk', 'gls', 'sl', 'slk']:
            car_model_formatted = f"{car_model_formatted}-klasa"
        elif car_model_formatted == 'ml':
            car_model_formatted = 'm-klasa'

    if generation:
        gen_parts = re.match(r"([A-Za-z0-9/ -]+) \(([\d-]+)\)", generation)
        if not gen_parts:
            return None

        gen_code, years = gen_parts.groups()
        gen_code = gen_code.split("/")[0].lower().replace(" ", "-")
        years = years.replace(")", "").replace("(", "").replace(" ", "")

        # Special case for Volkswagen Polo V
        if car_make_formatted == "volkswagen" and car_model_formatted == "polo" and gen_code == "v":
            years = years.split("-")[0]  # Take only the starting year

        if years.endswith("-"):
            years = years.rstrip("-")

        final_url = f"{base_url}/{car_make_formatted}/{car_model_formatted}?search%5Bfilter_enum_generation%5D=gen-{gen_code}-{years}"
    else:
        final_url = f"{base_url}/{car_make_formatted}/{car_model_formatted}"

    return final_url

def get_car_models(car_make):
    logging.debug(f"Fetching models for car make: {car_make}")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280,1024")
    chrome_service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    try:
        # Navigate to the website
        url = f"https://www.otomoto.pl/osobowe/{car_make.lower()}"
        logging.debug(f"Navigating to the URL for make: {car_make}")
        driver.get(url)
        time.sleep(2)
        driver.save_screenshot('01_initial_load.png')

        # Accept cookies if the button is present
        try:
            logging.debug("Checking for the cookies acceptance button")
            accept_cookies_button = driver.find_element(By.ID, 'onetrust-accept-btn-handler')
            if accept_cookies_button.is_displayed() and accept_cookies_button.is_enabled():
                accept_cookies_button.click()
                logging.debug("Cookies acceptance button clicked")
                time.sleep(2)
                driver.save_screenshot('02_after_accepting_cookies.png')
        except Exception as e:
            logging.debug(f"No cookies acceptance button found: {e}")

        # Wait for the input field to be present
        logging.debug("Waiting for the model input field to be present")
        model_input = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Model pojazdu"]')
        if model_input.is_displayed() and model_input.is_enabled():
            model_input.click()
            logging.debug("Model input field clicked")
            time.sleep(2)
            driver.save_screenshot('03_model_input_clicked.png')

        # Fetch car models
        logging.debug("Fetching car models")
        model_elements = driver.find_elements(By.CSS_SELECTOR, 'p.ooa-6y8xco.er34gjf0')
        models = [element.text.split(' (')[0] for element in model_elements if element.text != 'Wszystkie modele']
        logging.debug(f"Found models: {models}")
        driver.save_screenshot('04_after_fetching_models.png')

        return models

    except Exception as e:
        logging.error(f"An error occurred while fetching models: {e}")
        return []
    finally:
        driver.quit()

def get_car_generations(car_make, car_model):
    logging.debug(f"Fetching generations for car make: {car_make}, model: {car_model}")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280,1024")
    chrome_service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    try:
        # Sanitize car model name for URL
        sanitized_model = sanitize_car_model(car_model)

        # Navigate to the website for the specific car model
        car_make_formatted = car_make.lower().replace(" ", "-").replace("&", "and")
        car_model_formatted = sanitized_model.lower()

        # Special case for Mercedes-Benz models starting with 'klasa'
        if car_make_formatted == "mercedes-benz":
            if car_model_formatted.startswith("klasa"):
                car_model_parts = car_model_formatted.split("-")
                car_model_formatted = f"{car_model_parts[1]}-{car_model_parts[0]}"
            elif car_model_formatted in ['cla', 'clk', 'cls', 'gl', 'gla', 'glb', 'glc', 'gle', 'glk', 'gls', 'ml', 'sl', 'slk']:
                car_model_formatted = f"{car_model_formatted}-klasa"
            elif car_model_formatted == 'ml':
                car_model_formatted = 'm-klasa'




        url = f"https://www.otomoto.pl/osobowe/{car_make_formatted}/{car_model_formatted}"
        logging.debug(f"Navigating to the URL for make: {car_make}, model: {car_model}")
        driver.get(url)
        time.sleep(2)
        driver.save_screenshot('01_model_page_load.png')

        # Accept cookies if the button is present
        try:
            logging.debug("Checking for the cookies acceptance button")
            accept_cookies_button = driver.find_element(By.ID, 'onetrust-accept-btn-handler')
            if accept_cookies_button.is_displayed() and accept_cookies_button.is_enabled():
                accept_cookies_button.click()
                logging.debug("Cookies acceptance button clicked")
                time.sleep(2)
                driver.save_screenshot('02_after_accepting_cookies_model_page.png')
        except Exception as e:
            logging.debug(f"No cookies acceptance button found: {e}")

        # Wait for the generation input field to be present
        logging.debug("Waiting for the generation input field to be present")
        generation_input = driver.find_element(By.CSS_SELECTOR, 'input[type="text"][value="Generacja"]')
        if generation_input.is_displayed() and generation_input.is_enabled():
            generation_input.click()
            logging.debug("Generation input field clicked")
            time.sleep(2)
            driver.save_screenshot('03_generation_input_clicked.png')

        # Fetch car generations
        logging.debug("Fetching car generations")
        generation_elements = driver.find_elements(By.CSS_SELECTOR, 'p.ooa-6y8xco.er34gjf0')
        generations = [element.text for element in generation_elements if element.text != 'Wszystkie generacje']
        logging.debug(f"Found generations: {generations}")
        driver.save_screenshot('04_after_fetching_generations.png')

        return generations

    except Exception as e:
        logging.error(f"An error occurred while fetching generations: {e}")
        return []
    finally:
        driver.quit()

import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def scrape_auctions(url):
    logging.debug(f"Scraping auctions from URL: {url}")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280,1024")
    chrome_service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    try:
        auctions = []

        while True:
            driver.get(url)
            time.sleep(2)

            # Get page source and parse with Beautiful Soup
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Locate all auction sections
            auction_sections = soup.select('article[data-id]')
            logging.debug(f"Found {len(auction_sections)} auction sections on the page")

            for auction in auction_sections:
                try:
                    # Extract engine size and horsepower
                    description_element = auction.select_one('p.ooa-1tku07r.er34gjf0')
                    if description_element:
                        description = description_element.get_text().split(' • ')
                        engine_size = description[0] if len(description) > 0 else None
                        horsepower = description[1] if len(description) > 1 else None
                    else:
                        raise ValueError("Missing engine size and horsepower")

                    # Extract mileage
                    mileage_element = auction.select_one('dd[data-parameter="mileage"]')
                    mileage = mileage_element.get_text() if mileage_element else None

                    # Extract gearbox type
                    gearbox_element = auction.select_one('dd[data-parameter="gearbox"]')
                    gearbox = gearbox_element.get_text() if gearbox_element else None

                    # Extract production year
                    production_year_element = auction.select_one('dd[data-parameter="year"]')
                    production_year = production_year_element.get_text() if production_year_element else None

                    # Extract fuel type
                    fuel_type_element = auction.select_one('dd[data-parameter="fuel_type"]')
                    fuel_type = fuel_type_element.get_text() if fuel_type_element else None

                    # Extract price (only if in PLN)
                    price_element = auction.select_one('h3.ooa-1n2paoq.er34gjf0')
                    currency_element = auction.select_one('p.ooa-8vn6i7.er34gjf0')
                    price = price_element.get_text() if currency_element and currency_element.get_text() == 'PLN' else None

                    if all([engine_size, horsepower, mileage, gearbox, production_year, fuel_type, price]):
                        auctions.append({
                            'engine_size': engine_size,
                            'horsepower': horsepower,
                            'mileage': mileage,
                            'gearbox': gearbox,
                            'production_year': production_year,
                            'fuel_type': fuel_type,
                            'price': price
                        })
                        logging.debug(f"Added auction: {auctions[-1]}")
                    else:
                        logging.debug("Skipping a listing due to missing information")
                except Exception as e:
                    logging.debug(f"Skipping a listing due to an error: {e}")

            logging.debug(f"Scraped {len(auctions)} auctions from the current page")

            # Check if there is a next page button
            try:
                next_page_button = driver.find_element(By.CSS_SELECTOR, 'li[data-testid="pagination-step-forwards"]:not(.pagination-item__disabled)')
                if next_page_button:
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_page_button)
                    driver.execute_script("arguments[0].click();", next_page_button)
                    time.sleep(2)  # wait for the next page to load
                    url = driver.current_url  # update the URL to the new page
                else:
                    break
            except Exception as e:
                logging.debug(f"No next page button found or unable to click it: {e}")
                break

        logging.debug(f"Total scraped auctions: {len(auctions)}")
        return auctions

    except Exception as e:
        logging.error(f"An error occurred while scraping auctions: {e}")
        return []
    finally:
        driver.quit()





