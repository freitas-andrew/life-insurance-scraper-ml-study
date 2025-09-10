# Standard libraries
import time
from contextlib import contextmanager
import platform
import shutil

# Third-party libraries
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

def init_driver(headless=True):
    """Initializes and returns a headless Chrome WebDriver instance.
    
    Args:
        headless (bool): If True (default), launches Chrome w/no GUI.
    Returns:
        webdriver.Chrome: Configured WebDriver instance.
    """

        # Detect whether Chrome or Chromium is available
    if shutil.which("google-chrome") or shutil.which("chrome"):
        chrome_type = ChromeType.GOOGLE
    elif shutil.which("chrome.exe"):  # Detect Windows Chrome from WSL
        chrome_type = ChromeType.GOOGLE
    elif shutil.which("chromium-browser") or shutil.which("chromium"):
        chrome_type = ChromeType.CHROMIUM
    else:
        raise RuntimeError(
            "Neither Google Chrome nor Chromium is installed on this system."
        )

    # Set up browser options
    options = Options()

    if headless:
        options.add_argument("--headless=new") # Run Chrome in headless mode (no visible UI)
    options.add_argument("--log-level=3") # Next options Supress Chromium-specific logs (doesn't affect scraping)
    options.add_argument("--disable-logging")
    options.add_argument("--disable-gpu")  
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")

    # Automatically downloads the matching Chromium driver (browser must be installed separately)
    service = Service(
        ChromeDriverManager(chrome_type=chrome_type).install(),
        log_path="NUL" if platform.system() == "Windows" else "/dev/null"
    )
    return webdriver.Chrome(service=service, options=options)

@contextmanager
def edit_page_context(driver, edit_node, edit_text, btn_node):
    """A context manager to open the edit page, allow user interactions, and close it when done.

    Args:
        edit_node (str): Node of the edit button.
        edit_text (str): Visible text of the "Edit" button.
        btn_node (str): Node of the update button.
    """
    try:
        # Scroll to top
        driver.execute_script("window.scrollTo(0, 0);")
        
        # Open the edit page
        driver.find_element(By.XPATH, f"//{edit_node}[contains(text(), '{edit_text}')]").click()
        time.sleep(1)  # Give time for the edit page to load
        
        # Yield control back to the user to interact with the page
        yield driver

    finally:
        # Waits up to 20 seconds until the "Update Quote Details" button is clickable, then clicks it
        update_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//{btn_node}[@type='submit']")) 
        )
        update_btn.click()
        time.sleep(1)
        
        
def select_dropdown(driver, field_name, value, by_visible_text=False):
    """Selects an option from a dropdown menu, either by visible text or value.

    Args:
        field_name (str): The 'name' attribute of the dropdown.
        value (str): The value or visible text to select.
        by_visible_text (bool): Whether to select by visible text (True) or value attribute (False).
    """
    try:
        # Locate the dropdown element by its name attribute
        dropdown_element = driver.find_element(By.NAME, field_name)
        dropdown_selector = Select(dropdown_element)
        
        # Scroll to element
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown_element)  
        # Choosing selection method
        if by_visible_text:
            dropdown_selector.select_by_visible_text(str(value))   # Select by text users see
        else:
            dropdown_selector.select_by_value(str(value))           # Select by HTML value attribute
        time.sleep(0.5)
    except Exception as e:
        print(f"Could not select '{value}' for '{field_name}': {e}") # Raising selection error
        raise
    

def select_checkbox(driver, xpath):
    """General function to select one of two mutually exclusive options from checboxes (e.g., gender, smoker status).
    
    Args:
        driver: Selenium WebDriver instance.
        xpath (str): xpath of checkbox object that matches to required option.
    """
    try:
        # Look for any clickable element with the target text
        element = driver.find_element(By.XPATH, xpath)   
        if not element.is_selected():
            element.click()
    except Exception as e:
        print(f"Failed to select checkbox option: {e}")
        raise
    

def text_input(driver, field_name, value, by_xpath=False):
    """Finds the input field by its name attribute and types the specified text into it.

    Args:
        field_name (str): The 'name' attribute for which to find the input field by.
        value (str): The text value to input into the field.
        by_xpath (bool): Whether to select by xpath (True) or name (False).
    """
    
    try:
        # Locating the input element by xpath
        if by_xpath == True:
            input_element = driver.find_element(By.XPATH, field_name)
        else:
            # Locating the input element using its name attribute
            input_element = driver.find_element(By.NAME, field_name)

        # Clearing existing text
        input_element.clear()

        # Sending input text
        input_element.send_keys(value)
    except Exception as e:
        print(f"Failed to input {value} into field: {e}")
        raise
    

def ensure_page_ready(driver, xpath):
    """Waits unti the loader disappears and page is interactable

    Args:
        driver (_type_): _description_
        xpath (_type_): _description_
    """
    WebDriverWait(driver, 20).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, xpath))
    )
    time.sleep(0.5)
    
                
        
        
    


