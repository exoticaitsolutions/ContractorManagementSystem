import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import re

NUMBER_OF_MEMBERS_SCRAP = 100
USERNAME = "rimikaexoticait@gmail.com"
PASSWORD = "asdf123@"
NUM_TABS = NUMBER_OF_MEMBERS_SCRAP  # Number of concurrent tabs

def login_facebook():
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    driver.get("https://www.facebook.com/")
    time.sleep(3)

    username = driver.find_element(By.XPATH, "//input[@name='email']")
    username.send_keys(USERNAME)

    password = driver.find_element(By.ID, "pass")
    password.send_keys(PASSWORD)

    login_button = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="royal_login_button"]')
    login_button.click()
    time.sleep(3)
    driver.get("https://www.facebook.com/groups/njcontractorsconnect")
    time.sleep(4)
    return driver

def scrape_profile_data(driver, profile_url):
    driver.execute_script(f"window.open('{profile_url}', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(4)
    
    try:
        name = driver.find_element(By.XPATH, '//div[@class="x78zum5 xdt5ytf x1wsgfga x9otpla"]//span')
        scrap_contact_info = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div')
        scrap_contact_info_text = scrap_contact_info.text
        formatted_contact_text = scrap_contact_info_text.replace('\n', '\n')
        profile_data = {
            "Name": name.text,
            "Contact Info": formatted_contact_text
        }
    except NoSuchElementException:
        print("Element not found on profile page.")
        profile_data = None
    finally:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
    
    return profile_data

def scrape_facebook_data():
    start_time = time.time()
    driver = login_facebook()
    
    link = driver.find_element(By.CSS_SELECTOR, 'a[href="/groups/2020285764874761/members/"]')
    link.click()
    time.sleep(3)
    
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.5);")
    time.sleep(2)

    contact_data_list = []
    member_ids = []
    processed_members = set()
    
    while len(contact_data_list) < NUMBER_OF_MEMBERS_SCRAP:
        try:
            # Scroll down to load more members
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Wait for new members to load
            
            all_members = driver.find_elements(By.XPATH, '//*[@class="html-div x11i5rnm x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1oo3vh0 x1rdy4ex"]')

            if not all_members:
                print("No members found. Exiting.")
                break

            # for mem in all_members:
            for j in range(2,len(all_members)):
                if len(contact_data_list) >= NUMBER_OF_MEMBERS_SCRAP:
                    break
                mem = all_members[j]
                member_name_element = mem.find_elements(By.XPATH, './/*[@class = "x78zum5 xdt5ytf xz62fqu x16ldp7u"]/div/span/span/span/a')
                print("Member name elements found: ", len(member_name_element))
                
                for member in member_name_element:
                    href_value = member.get_attribute('href')
                    match = re.search(r'user/(.*?)/', href_value)
                    if match:
                        member_id = match.group(1)

                        if href_value in processed_members:
                            continue

                        processed_members.add(href_value)
                        member_ids.append(member_id)

                        if len(member_ids) >= NUMBER_OF_MEMBERS_SCRAP:
                            break
                if len(member_ids) >= NUMBER_OF_MEMBERS_SCRAP:
                    break
            if len(member_ids) >= NUMBER_OF_MEMBERS_SCRAP:
                break

        except Exception as e:
            print("Error occurred:", e)
            break

    # Handle tabs sequentially
    num_tabs = min(NUM_TABS, len(member_ids))
    driver.execute_script("window.open('');")  # Open a new tab
    driver.switch_to.window(driver.window_handles[-1])
    driver.get("about:blank")  # Create a new blank tab

    for i, member_id in enumerate(member_ids[:NUMBER_OF_MEMBERS_SCRAP]):
        if i % num_tabs == 0 and i != 0:
            # Wait for all tabs to complete before opening new ones
            print("Waiting for tabs to complete...")
            time.sleep(10)

        profile_url = f"https://www.facebook.com/profile.php?id={member_id}&sk=about_contact_and_basic_info"
        profile_data = scrape_profile_data(driver, profile_url)
        
        if profile_data:
            contact_data_list.append(profile_data)
            print(f"Profile data scraped: {profile_data}")
            print(f"Profile data length: {len(contact_data_list)}")

    driver.quit()
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total execution time: {total_time:.2f} seconds")

    # Write to CSV
    with open('facebook_members_data1.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Name', 'Contact Info']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for member in contact_data_list:
            writer.writerow(member)

    # Load the CSV file into a DataFrame
    df = pd.read_csv("facebook_members_data1.csv")

    # Initialize new columns
    df["Phone Number"] = ""
    df["Email"] = ""
    df["Website URL"] = ""
    df["Address"] = ""

    # Define regex patterns for email, phone numbers, URLs, and addresses
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    phone_pattern = r"\+?\d[\d -]{8,}\d"
    url_pattern = (
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    )
    address_pattern = r"(?<=Contact info\n)(.*\nAddress)"

    # Function to extract and assign data to new columns
    def extract_info(contact_info):
        if not isinstance(contact_info, str):
            contact_info = ""

        # Extract email, phone number, and URL
        email = re.findall(email_pattern, contact_info)
        phone = re.findall(phone_pattern, contact_info)
        url = re.findall(url_pattern, contact_info)

        # Extract address (Assuming the address is always preceded by "Contact info")
        address_match = re.search(address_pattern, contact_info, re.MULTILINE)
        address = address_match.group(1) if address_match else ""

        # Return appropriate values
        return pd.Series(
            {
                "Email": email[0] if email else "",
                "Phone Number": phone[0] if phone else "",
                "Website URL": url[0] if url else "",
                "Address": address.strip() if address else "",
            }
        )     

    # Apply the extraction function to each row
    df[["Email", "Phone Number", "Website URL", "Address"]] = df["Contact Info"].apply(
        extract_info
    )

    # Drop the 'Contact Info' column
    df = df.drop(columns=["Contact Info"])
    final_csv = 'final_facebook_member_data1.csv'

    # Save the DataFrame to a new CSV file
    df.to_csv(final_csv, index=False)

    print(f"Data extraction complete. Updated file saved as {final_csv}.")

scrape_facebook_data()
