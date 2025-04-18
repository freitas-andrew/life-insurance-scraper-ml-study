# Standard libraries
import time
from contextlib import contextmanager

# Third-party libraries
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def init_driver(headless=True):
    """
    Initializes and returns a headless Chrome WebDriver instance.
    
    Args:
    headless (bool): If True (default), launches Chrome w/no GUI.

    """
    # Set up browser options
    options = Options()
    if headless:
        options.add_argument("--headless") # Run Chrome in headless mode (no visible UI)
        options.add_argument("--log-level=3") # Supress most low-level Chromium logs (don't affect scraping)
    return webdriver.Chrome(service=Service(ChromeDriverManager().install(), log_path="NUL"), options=options) # Automatically installs WebDriver if not installed


@contextmanager
def edit_page_context(driver, edit_text):
    """
    A context manager to open the edit page, allow user interactions, and close it when done.

    Args:
        driver: Selenium WebDriver instance.
        edit_text (str): Visible text of the "Edit" button.
    """
    try:
        # Scroll to top
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)
        
        # Open the edit page
        driver.find_element(By.XPATH, f"//a[contains(text(), '{edit_text}')]").click()
        time.sleep(1)  # Give time for the page to load
        
        # Yield control back to the user to interact with the page
        yield driver

    finally:
        # Waits up to 0.5 seconds until the "Update Quote Details" button is clickable, then clicks it
        update_btn = WebDriverWait(driver, 0.5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Update Quote Details')]")) #TODO: what does this do?
        )
        update_btn.click()
        time.sleep(3)
        
        
def select_dropdown(driver, field_name, value, by_visible_text=False):
    """
    Selects an option from a dropdown menu, either by visible text or value.

    Args:
        driver: Selenium WebDriver instance.
        tag_name (str): The 'name' attribute of the dropdown.
        value (str): The value or visible text to select.
        by_visible_text (bool): Whether to select by visible text (True) or value attribute (False).
    """
    try:
        # Scroll to top
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)
        
        # Locate the dropdown element by its name attribute
        dropdown_element = driver.find_element(By.NAME, field_name)
        dropdown_selector = Select(dropdown_element)
        
        # Choosing selection method
        if by_visible_text:
            dropdown_selector.select_by_visible_text(str(value))   # Select by text users see
        else:
            dropdown_selector.select_by_value(str(value))          # Select by HTML value attribute
        time.sleep(0.5)
        
    except Exception as e:
        print(f"Could not select '{value}' for '{field_name}': {e}") # Raising selection error
        raise
    

def select_checkbox(driver, option_text):
    """
    General function to select one of two mutually exclusive options from checboxes (e.g., gender, smoker status).
    
    Args:
        driver: Selenium WebDriver instance.
        option_text (dict): visible text of the checkbox that needs to be clicked.
    """
    try:
        # Look for any clickable element with the target text
        xpath = f"//*[normalize-space(text())='{option_text}']"
        element = driver.find_element(By.XPATH, xpath)      
        if not element.is_selected():
            element.click() # Click the option if not already clicked
        time.sleep(0.5)
            
    except Exception as e:
        print(f"Failed to select checkbox option: {option_text}")
        raise



