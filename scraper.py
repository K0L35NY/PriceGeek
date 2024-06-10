import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.DEBUG)

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
        models = [element.text.split(' (')[0] for element in model_elements]

        # Remove the first element if it's "Wszystkie modele"
        if models and models[0] == "Wszystkie modele":
            models.pop(0)
            logging.debug("Removed 'Wszystkie modele' from the list")

        logging.debug(f"Found models: {models}")
        driver.save_screenshot('04_after_fetching_models.png')

        return models

    except Exception as e:
        logging.error(f"An error occurred while fetching models: {e}")
        return []
    finally:
        driver.quit()
