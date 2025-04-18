# Standard libraries
import csv
import time
from datetime import datetime

# Third-party libraries
from selenium.webdriver.common.by import By

# Local imports
from utils import * # Imports init_driver, edit_page_context, select_dropdown, select_checkbox and entire data sample

def main():
    quote_url = "https://quoter.lifeinsure.com/results?quote=fbSu2A4b44Pfg7WkYqUiBx2KPfVafAUM" # lifeinsure quote w/preset BMI, Health Rating and 1st Jan DOB

    driver = init_driver() # Initialising driver 
    with driver:
        driver.get(quote_url)
        results, failed = scrape_combinations(driver, coverage_amounts, term_lengths, ages, genders, nicotine_status, states)
        
        # Retry a maximum of 5 times until success
        for _ in range(5):
            if not failed:
                break
            print("🔁 Retrying failed combos...")
            new_failed = []
            for combo in failed:
                driver.get(quote_url)  # ← reloading the page
                # Unpacks each item in "combo" into separate single-item lists for passing to scrape_combinations
                partial_results, partial_failed = scrape_combinations(driver, *[[x] for x in combo]) 
                print(f"After retry: {partial_results}")
                results.extend(partial_results)      # Adding to results
                new_failed.extend(partial_failed)    # Collecting still-failing combos
            failed = new_failed                      # Retry remaining ones next round
            
            
    file_name = "US_quotes.csv"
    with open(file_name, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Coverage Amount", "Term Length", "Age", "Gender", "Is_Smoker", "State", "Premium"])
        writer.writerows(results)

    print(f"📁 All done — exported to '{file_name}'")
    
    
def scrape_combinations(driver, coverage_amounts, term_lengths, ages, genders, nicotine_status, states):
    """
    Iterates through combinations of inputs and collects premiums.

    Returns:
        List of tuples containing input parameters and corresponding premiums.
    """
    all_data = []
    failed_combos = []
    time.sleep(1)

    # Iterating through each possible combo of variables
    for coverage in coverage_amounts:
        for term in term_lengths:
            for age in ages:
                for gender in genders:
                    for r_nicotine in nicotine_status:
                        for state in states:
                            # Calculating birth year corresponding to given age (using 1st of Jan as baseline)
                            birth_year = str(datetime.now().year - age)
                            try:
                                # Selecting coverage amount and term length
                                select_dropdown(driver, field_name="coverage_amount", value=coverage)
                                select_dropdown(driver, field_name="category_code", value=term, by_visible_text=True)
                                # Opening the edit page and selecting relevant dropdowns for current combo
                                with edit_page_context(driver, edit_text='Edit'):
                                    select_dropdown(driver, field_name="state", value=state)
                                    select_dropdown(driver, field_name="tobaccotime", value=r_nicotine, by_visible_text=True)
                                    select_dropdown(driver, field_name="dob_year", value=birth_year)
                                    select_checkbox(driver, option_text=gender)
                                    
                                # Extracting each premium corresponding to this combo profile
                                premiums = extract_premiums(driver)
                                
                                # Appending data to our list (if premiums is empty nothing is appended)
                                for premium in premiums:
                                    all_data.append((coverage, term, age, gender, r_nicotine, state, premium))

                                print(f"✅ Done: {coverage}, {term}: Age {age}, {gender}, {r_nicotine}, {state} ") # Printing current combo completed
                            except Exception as e:
                                print(f"❌ Error on combo: {coverage}, {term}: Age {age}, {gender}, {r_nicotine}, {state}: {e}")
                                failed_combos.append((coverage, term, age, gender, r_nicotine, state)) # Recording failed combos
                                continue
    return all_data, failed_combos


def extract_premiums(driver):
    """
    Extracts available premiums from the 'No Medical Exam Policies' section.

    Returns:
        List of multiple premium strings (e.g., ['$14.32']) for each combo.
    """
    premiums = []
    time.sleep(1)
    try:
        no_me_header = driver.find_element(By.XPATH, "//div[contains(text(), 'No Medical Exam Policies')]") # Find the header 'No Medical Exam Policies'
        no_me_section = no_me_header.find_element(By.XPATH, "..") # Go to the parent div
    except:
        print("⏭️ Skipping: No quotes found.") # If header isn't present, implies no quotes under no_me
        return premiums

    # Try to expand more results
    try:
        show_more_button = no_me_section.find_element(By.XPATH, ".//a[contains(text(), 'View')]")
        show_more_button.click()
        time.sleep(0.5)
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