# Standard libraries
import csv
import time
from datetime import datetime
from pathlib import Path

# Third-party libraries
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Local imports
from utils import * # Imports init_driver, edit_page_context, select_dropdown, select_checkbox, text_input, ensure_page_ready and entire data sample

def main():
    # Initial quote form which asks for risk information: age, gender, and nicotine status (quotes are on page after) 
    quote_form = "https://www.drewberryinsurance.co.uk/life-insurance/life-insurance-quote"
    
    driver = init_driver() # Initialising driver
    
    # Path of CSV w/URLs and their data
    u_file_name = "drewberry_urls.csv"
    urls_csv = Path(__file__).resolve().parent.parent / "data" / "raw" / u_file_name
    expected_rows = len(ages) * len(genders) * len(nicotine_status) + 1  # +1 for header
    
    # Check if file exists or if number of rows matches number of expected combinations
    if not urls_csv.exists() or sum(1 for _ in open(urls_csv, "r")) != expected_rows:
        print("▶️  Collecting URLs...")
        with driver:
            url_results = extract_risk_info(driver, quote_form, ages, genders, nicotine_status)
        driver = init_driver() # Initialising driver again (because it closed)
        
        # Saving to CSV
        with open(urls_csv, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Age", "Gender", "Nicotine Use", "URL"])  # CSV header
            writer.writerows(url_results)    
        print(f"📁 URLs saved to '{u_file_name}', in {urls_csv}")
    else:
        print("↪️  URL collection already complete - skipping collection.")
    
    
    # Opening CSV with our URLs and their associated risk info.
    with open(urls_csv, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
    
        results = []
        failed = []
        with driver:
            for row in reader:
                # Calling the scrape_combos function to get the current iteration's results and failed combos
                current_results, current_failed = scrape_combos(driver, row["URL"], coverage_amounts, term_lengths, row["Age"], row["Gender"], row["Nicotine Use"])
                
                # Appending the current iteration's results and failed combos to the existing lists
                results.extend(current_results)
                failed.extend(current_failed)
        
            # Retry a maximum of 5 times until success
            for i in range(1, 6):
                if not failed:
                    break
                print(f"🔁 Retrying failed combos... ({i})")
                new_failed = []
                for combo in failed:
                    # Run the scraping function with specific inputs
                    retry_results, retry_failed = scrape_combos(driver, combo[5], [combo[0]], [combo[1]], combo[2], combo[3], combo[4])
                    results.extend(retry_results)
                    new_failed.extend(retry_failed)
                failed = new_failed # Retry remaining ones next round

    file_name = "UK_quotes.csv"
    # Explicitly stating file path (../data/raw/{file_name} is done relative to console's current directory)
    output_path = Path(__file__).resolve().parent.parent / "data" / "raw" / file_name
    # Saving to csv, encoding="utf-8" needed for reading and writing "£"
    with open(output_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Coverage Amount", "Term Length", "Age", "Gender", "Is_Smoker", "Premium"])
        writer.writerows(results)
    print(f"📁 All done — exported to '{file_name}', in {output_path}")


def extract_risk_info(driver, quote_form, ages, genders, nicotine_status):
    """Inputs risk info into form and extracts the associated URL for each risk combo.

    Args:
        quote_form (str): URL of quote form.
        var_name (list): takes in lists for (age, gender, and nicotine_status), for which to form combos.

    Returns:
        url_results: list of tuples containing URLs and their associated risk info.
    """
    url_results = []
    
    for age in ages:
        for gender in genders:
            for nic in nicotine_status:
                try:
                    # Calculating birth year corresponding to given age (using 1st of Jan as baseline)
                    birth_year = str(datetime.now().year - age)
                    
                    # Go to the form page for every new combo
                    driver.get(quote_form)
                    
                    # Clicking 'Deny' button for cookies
                    try:
                        driver.find_element(By.XPATH, "//span[text()='Deny']").click()
                    except:
                        pass  # If cookie popup doesn't appear (likely won't after first time)
                    
                    # We select Level cover (for simplicity and to enable fair comparison w/ US data)
                    select_checkbox(driver, xpath=f"//input[@type='radio' and @value='Level']")
                    # Selecting smoker/non-smoker
                    select_checkbox(driver, xpath=f"//input[@type='radio' and @value='{nic}']")
                    
                    # Occupation field is both a text and dropdown field
                    input_field = driver.find_element(By.ID, "react-select-Occupation__c-input")
                    # Click the dropdown to activate it
                    input_field.click()
                    # Selection no occupation, again for fair comparison with US, where this isn't present
                    input_field.send_keys("Other - Occupation not listed")
                    # Finally press "enter" to submit into field
                    input_field.send_keys(Keys.ENTER)

                    # 1st pf Jan as base, then we vary year
                    text_input(driver, field_name="dateDD", value="01")
                    text_input(driver, field_name="dateMM", value="01")
                    text_input(driver, field_name="dateYYYY", value=birth_year)
                    
                    # Inputting placeholder data
                    text_input(driver, field_name="FirstName", value="John")
                    text_input(driver, field_name="LastName", value="Doe")
                    driver.find_element(By.CSS_SELECTOR, '[data-test="TS_INPUT_FORM_PHONE"]').send_keys("07386411071") # Temporary UK phone number
                    text_input(driver, field_name="email", value="placeholder@nowhere.org")
                    
                    # Selecting gender
                    select_checkbox(driver, xpath=f"//input[@type='radio' and @value='{gender}']")
                    
                    # Clicking T&C checkbox
                    driver.find_element(By.NAME, "check-privacy").click()
                    
                    # Submitting, then waiting for next page to load
                    driver.find_element(By.XPATH, "//input[@type='submit']").click()
                    WebDriverWait(driver, 15).until(
                    EC.invisibility_of_element_located((By.XPATH, "//input[@value='Please Wait...']"))
                    )
                    # ensure_page_ready(driver, xpath="//input[@value='Please Wait...']")
                    time.sleep(0.5)
                    
                    # Extracting our url and then storing our data
                    current_url = driver.current_url
                    url_results.append((age, gender, nic, current_url))
                    print(f"✅ Collected Url for: Age {age}, {gender}, {nic}")

                except Exception as e:
                    print(f"❌ Error Collecting Url for: Age {age}, {gender}, {nic}: {e}")
    return url_results
                

def scrape_combos(driver, current_url, coverage_amounts, term_lengths, age, gender, nic):
    """Iterates through combinations of inputs and collects premiums.

    Args:
        current_url (str): current url of combo.
        coverage_amounts, term_lengths (list): lists of variables to input.
        age, gender, nic (str): risk info. associated with current URL.
    Returns:
        all_data (list): List of tuples containing input parameters and corresponding premiums.
        failed_combos (list):  list of tuples containing input parameters abd url for which scraping failed.
    """
    all_data = []
    failed_combos = []
    
    # Inputting our already collected URL
    driver.get(current_url)
    ensure_page_ready(driver, xpath="[data-test='TS_FULL_LOADER_MODAL']")
    # Close intial page sign in prompt (only appears when first opening URL)
    try:
        driver.find_element(By.CSS_SELECTOR, '[data-test="TS_CLOSE_MODAL"]').click()
    except:
        pass
    ensure_page_ready(driver, xpath="[data-test='TS_BACKDROP']") 
    
    
    
    
    for coverage in coverage_amounts:
        for term in term_lengths:
            try:
                # Opening the edit page and inputting cover and term duration
                with edit_page_context(driver, edit_node="span", edit_text="Edit Quotes", btn_node="input"):
                    text_input(driver, field_name="initialLifeCover", value=coverage)
                    text_input(driver, field_name="TermYears", value=term)
                # Wait for page to be ready after clicking 'Submit'
                ensure_page_ready(driver, xpath="[data-test='TS_FULL_LOADER_MODAL']")
                ensure_page_ready(driver, xpath="[data-test='TS_BACKDROP']") 
                
                # Extracting each premium corresponding to this risk profile
                premiums = extract_premiums(driver)
                
                # Appending data to our list (if premiums is empty nothing is appended)
                for premium in premiums:
                    all_data.append((coverage, term, age, gender, nic, premium))
                
                if premiums:
                    print(f"✅ Done: {coverage}, {term}: Age {age}, {gender}, {nic}") # Printing current combo completed        
                else:
                    print(f"⏭️  Skipping: No quotes found for {coverage}, {term}, Year Term: Age {age}, {gender}, {nic}")
                    
            except Exception as e:
                print(f"❌ Error on combo: {coverage}, {term}: Age {age}, {gender}, {nic}: {e}")
                failed_combos.append((coverage, term, age, gender, nic, current_url)) # Recording failed combos
                continue
    return all_data, failed_combos
    
    
def extract_premiums(driver):
    """
    Extracts available premiums from the 'Life Insurance Only' section.

    Returns:
        List of multiple premium strings (e.g., ['$14.32']) for each combo.
    """
    ensure_page_ready(driver, xpath="[data-test='TS_FULL_LOADER_MODAL']")
    premiums = []
    
    # Click the "Life Insurance Only" filter button
    driver.find_element(By.ID, "life-only").click()
    
    # Try to expand more results by clicking "Show More" button
    try:
        show_more_button = driver.find_element(By.XPATH, ".//span[contains(text(), 'Show More')]")
        show_more_button.click()
    except:
        pass  # Ignore if "Show More" button not present
    
    # find all quote entries and puts it in a list
    quote_entries = driver.find_elements(By.XPATH, "//span[contains(@class, 'QuoteCardContent_Price')]")
    
    if not quote_entries:
        pass # If no quote entries, pass and let empty string be passed 
    else:
        for entry in quote_entries:
            premiums.append(entry.text) # Append only the text (the premiums)
    return premiums
    

if __name__ == "__main__":
    main()