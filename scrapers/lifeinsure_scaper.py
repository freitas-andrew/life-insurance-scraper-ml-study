# Standard libraries
import csv
from datetime import datetime
from pathlib import Path
import time

# Third-party libraries
from selenium.webdriver.common.by import By

# Local imports
from utils import * # Imports init_driver, edit_page_context, select_dropdown, select_checkbox, text_input, ensure_page_ready and entire data sample

"""
IMPORTANT NOTE:
At the time of data collection, the site https://quoter.lifeinsure.com did not and still does not appear to have scraping restrictions in place — either via
a restrictive robots.txt file or active enforcement mechanisms. Scraping was conducted carefully and responsibly over multiple days without interuption, 
indicating that restrictions were absent or not actively enforced during that period. However, an eventual IP block (which only occurred after the aforementioned 
prolonged access), suggests that stricter anti-bot measures were introduced after the main bulk of the data collection, or that excessive scraping raised a flag.

CAUTION: 
Although the scraping programme still works — and limited scrapinng seems to garner no immediate action — future scraping attempts (especially in high volumes) on this site 
may lead to an IP ban for this website, or other enforcement actions, as current restrictions appear to be more aggressive than during the original data collection. 
"""


def main():
    # lifeinsure quote portal
    quote_url = "https://quoter.lifeinsure.com/#gender" 
    
    nicotine_status = ["Current user", "Never Used"] # Required format for matching later
    
    # Using global to avoid UnboundLocalError when modifying imported variable
    global term_lengths
    term_lengths = [f"{term} Year Term" for term in term_lengths] # Required format for matching later
    
    driver = init_driver() # Initialising driver 
    with driver:
        results, failed = scrape_combos(driver, quote_url, coverage_amounts, term_lengths, ages, genders, nicotine_status)
        
        # Retry a maximum of 10 times until success
        for i in range(1, 11):
            if not failed:
                break
            print(f"🔁 Retrying failed combos... ({i})")
            new_failed = []
            for combo in failed:
                # Unpacks each item in "combo" into separate single-item lists for passing to scrape_combinations
                retry_results, retry_failed = scrape_combos(driver, quote_url, *[[x] for x in combo])
                results.extend(retry_results)      # Adding to results
                new_failed.extend(retry_failed)    # Collecting still-failing combos
            failed = new_failed                    # Retry remaining ones next round
            
    file_name = "US_quotes.csv"
    # Explicitly stating file path (../data/raw/{file_name} is done relative to console's current directory)
    output_path = Path(__file__).resolve().parent.parent / "data" / "raw" / file_name
    # Saving to CSV
    with open(output_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Coverage Amount", "Term Length", "Age", "Gender", "Is_Smoker", "Premium"]) # CSV header
        writer.writerows(results)
    print(f"📁 All done — exported to '{file_name}', in {output_path}")
    
    
def scrape_combos(driver, quote_url, coverage_amounts, term_lengths, ages, genders, nicotine_status):
    """Iterates through combinations of inputs and collects premiums.

    Args:
        quote_url (str): URL of quote website (has premiums and risk editing on same page)
        var_name (list): takes in multiple lists of variables to form each combo, and collect their premiums.
        
    Returns:
        all_data (list): List of tuples containing input parameters and corresponding premiums.
        failed_combos (list): list of tuples containing input parameters for which scraping failed.
    """
    all_data = []
    failed_combos = []
    
    driver.get(quote_url) # Reloading the page
    
    # Filling out initial form to have preset BMI, Health Rating, 1st Jan DOB and State as Alabama (upon analysis, state does not affect premiums)
    time.sleep(1)
    select_checkbox(driver, xpath="/html/body/div[1]/div[3]/form/div[1]/div[4]/label[1]/strong/span") # Selecting Male
    time.sleep(1)
    select_dropdown(driver, field_name="coverage", value="100000",) # Selection $100,000 cover
    time.sleep(1)
    select_checkbox(driver, xpath="/html/body/div[1]/div[3]/form/div[3]/div[4]/label[1]/strong/span") # Selecting 10 Year Term
    time.sleep(1)
    select_dropdown(driver, field_name="state", value="Alabama", by_visible_text=True) # Selecting stateas Alabama
    time.sleep(1)
    select_checkbox(driver, xpath="/html/body/div[1]/div[3]/form/div[5]/div[4]/label[1]/strong") # Selecting "No" to used nicotine products
    time.sleep(1)
    # Selecting month, day and year of birth
    text_input(driver, field_name='//*[@id="mm"]', value="1", by_xpath=True)
    text_input(driver, field_name='//*[@id="dd"]', value="1", by_xpath=True)
    text_input(driver, field_name='//*[@id="yyyy"]', value="2000", by_xpath=True)
    time.sleep(1)
    # Inputting average height and weight which correspond to an average BMI
    text_input(driver, field_name="height", value="510")
    text_input(driver, field_name="weight", value="167")
    time.sleep(1)
    # Selecting average health
    select_checkbox(driver, xpath="/html/body/div[1]/div[3]/form/div[9]/div[4]/div[2]/label/strong")
    
    ensure_page_ready(driver, xpath="div[x-show='loading && !resultsModalOpen']")
    
    

    # Iterating through each possible combo of variables
    for coverage in coverage_amounts:
        for term in term_lengths:
            for age in ages:
                for gender in genders:
                    for nic in nicotine_status:
                        # Calculating birth year corresponding to given age (using 1st of Jan as baseline)
                        birth_year = str(datetime.now().year - age)
                        try:
                            # Selecting coverage amount and term length
                            select_dropdown(driver, field_name="coverage_amount", value=coverage)
                            ensure_page_ready(driver, xpath="div[x-show='loading && !resultsModalOpen']")
                            # Scroll to top to make sure term dropdown is visible
                            driver.execute_script("window.scrollTo(0, 0);")
                            select_dropdown(driver, field_name="category_code", value=term, by_visible_text=True)
                            ensure_page_ready(driver, xpath="div[x-show='loading && !resultsModalOpen']")
                            # Opening the edit page and selecting relevant dropdowns for current combo
                            with edit_page_context(driver, edit_node="a", edit_text="Edit", btn_node="button"):
                                select_dropdown(driver, field_name="tobaccotime", value=nic, by_visible_text=True)
                                select_dropdown(driver, field_name="dob_year", value=birth_year)
                                select_checkbox(driver, xpath=f"//*[normalize-space(text())='{gender}']")
                            ensure_page_ready(driver, xpath="div[x-show='loading && !resultsModalOpen']")
                            # Extracting each premium corresponding to this risk profile
                            premiums = extract_premiums(driver)
                            
                            # Appending data to our list (if premiums is empty nothing is appended)
                            for premium in premiums:
                                all_data.append((coverage, term, age, gender, nic, premium))

                            if premiums:
                                print(f"✅ Done: {coverage}, {term} Year Term: Age {age}, {gender}, {nic}") # Printing current combo completed
                            else:
                                print(f"⏭️  Skipping: No quotes found for {coverage}, {term}, Year Term: Age {age}, {gender}, {nic}")
                                
                        except Exception as e:
                            print(f"❌ Error on combo: {coverage}, {term}: Age {age}, {gender}, {nic}: {e}")
                            failed_combos.append((coverage, term, age, gender, nic)) # Recording failed combos
                            continue
    return all_data, failed_combos


def extract_premiums(driver):
    """Extracts available premiums from the 'No Medical Exam Policies' section.

    Returns:
        premiums: List of multiple premium strings (e.g., ['$14.32']) for each combo.
    """
    premiums = []
    
    no_results_elem = driver.find_element(By.XPATH, "//h2[contains(text(), 'Your original search had no results')]")
    # If 'no results' element is visibly displayed return empty premiums list
    if no_results_elem.is_displayed():
        return premiums
    
    try:
        # Find the header 'No Medical Exam Policies'
        no_me_header = driver.find_element(By.XPATH, "//div[contains(text(), 'No Medical Exam Policies')]") 
        no_me_section = no_me_header.find_element(By.XPATH, "..") # Go to the parent div
    except:
        return premiums # Return nothing, as if header isn't present, implies no quotes under no_me

    # Try to expand more results by clicking "View more" button
    try:
        no_me_section.find_element(By.XPATH, ".//a[contains(text(), 'View')]").click()
    except:
        pass  # Ignore if "View more" button not present

    # Collect premium parts, specifically under no_me section
    dollar_spans = no_me_section.find_elements(By.XPATH, ".//span[@x-text=\"getModalPrice(row, paymentMode).split('.')[0]\"]")
    cent_spans = no_me_section.find_elements(By.XPATH, ".//span[@x-text=\"getModalPrice(row, paymentMode).split('.')[1]\"]")

    # Pairs dollar and cent values, formats them as "$d.c", and filters out empty values
    premiums = [
        f"${d}.{c}"
        for d, c in zip(
            (dollar.text.strip() for dollar in dollar_spans),
            (cent.text.strip() for cent in cent_spans)
        ) if d and c
    ]
    return premiums


if __name__ == "__main__":
    main()