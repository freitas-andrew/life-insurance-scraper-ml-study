from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

# Set up browser options
options = Options()
options.add_argument("--headless") # Hides opening of new chrome tab

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

with driver as driver:
    # Load the quote results page
    url = "https://quoter.lifeinsure.com/results?quote=fbSu2A4b44Pfg7WkYqUiBx2KPfVafAUM"
    driver.get(url)
    time.sleep(10)

    # Try to find the "No Medical Exam Policies" title div, continue only if found
    try:
        no_me_header = driver.find_element(By.XPATH, "//div[contains(text(), 'No Medical Exam Policies')]")
        no_me_section = no_me_header.find_element(By.XPATH, "..")  # finding parent section
    except:
        print("Skipping: No quotes found.")
        driver.quit()
        exit() # 
        
    # Try clicking "View more results" button inside this section
    try:
        show_more_button = no_me_section.find_element(By.XPATH, ".//a[contains(text(), 'View')]")
        show_more_button.click()
        # time.sleep(1)  # Wait for more results to load
    except:
        pass # Otherwise continue on as normal

    # Now find the premium spans inside that section
    dollar_spans = no_me_section.find_elements(By.XPATH, ".//span[@x-text=\"getModalPrice(row, paymentMode).split('.')[0]\"]")
    cent_spans   = no_me_section.find_elements(By.XPATH, ".//span[@x-text=\"getModalPrice(row, paymentMode).split('.')[1]\"]")

    # Extract the text from the spans
    extracted_premiums = []
    for dollar, cent in zip(dollar_spans, cent_spans):
        dollars = dollar.text.strip()
        cents = cent.text.strip()
        if dollars and cents:
            extracted_premiums.append(f"${dollars}.{cents}")

    # Saving to .csv
    with open("premiums.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        for premium in extracted_premiums:
            writer.writerow([premium])

