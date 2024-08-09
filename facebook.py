import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, ElementClickInterceptedException
from time import sleep
import pandas as pd
import re

NUMBER_OF_MEMBERS_SCRAP = 5
USERNAME = "abhishek@exoticaitsolutions.com"
PASSWORD = "asdf123@"

def type_like_human(element, text):
    """Simulates human typing by sending one character at a time."""
    for character in text:
        element.send_keys(character)
        sleep(0.1)  # Optional: Add delay for more human-like typing

def wait_for_element(driver, by, value, timeout=10):
    """Waits for an element to be present and returns it."""
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))

def wait_for_clickable_element(driver, by, value, timeout=10):
    """Waits for an element to be clickable and returns it."""
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))

def wait_for_elements(driver, by, value, timeout=10):
    """Waits for all elements matching the locator to be present and returns them."""
    return WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((by, value)))

def scroll_into_view(driver, element):
    """Scrolls the element into the visible area."""
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    sleep(1)

def click_with_retry(driver, element, retries=3):
    """Tries clicking an element, with retries if intercepted by other elements."""
    for attempt in range(retries):
        try:
            element.click()
            return True
        except ElementClickInterceptedException:
            print(f"Click intercepted, retrying... (Attempt {attempt + 1}/{retries})")
            sleep(2)
    print("Failed to click the element after retries.")
    return False

def scrape_facebook_data():
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    driver.get("https://www.facebook.com/")
    sleep(3)

    # Enter username
    username = wait_for_element(driver, By.XPATH, "//input[@name='email']")
    ActionChains(driver).move_to_element(username).click().perform()
    type_like_human(username, USERNAME)
    print("Username filled successfully")

    # Enter password
    password = wait_for_element(driver, By.ID, "pass")
    ActionChains(driver).move_to_element(password).click().perform()
    type_like_human(password, PASSWORD)
    print("Password filled successfully")

    # Click login button
    login_button = wait_for_clickable_element(driver, By.CSS_SELECTOR, 'button[data-testid="royal_login_button"]')
    login_button.click()
    sleep(3)
    driver.get("https://www.facebook.com/groups/njcontractorsconnect")
    sleep(4)

    link = wait_for_clickable_element(driver, By.CSS_SELECTOR, 'a[href="/groups/2020285764874761/members/"]')
    link.click()
    sleep(5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.3);")
    sleep(4)

    member_list = []
    processed_members = set()


    while len(member_list) < NUMBER_OF_MEMBERS_SCRAP:
        try:
            # Refetch the list of members
            all_members = wait_for_elements(driver, By.XPATH, '//*[@class="html-div x11i5rnm x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1oo3vh0 x1rdy4ex"]')

            if not all_members:
                print("No members found. Exiting.")
                break

            for i in range(len(all_members)):
                if len(member_list) >= NUMBER_OF_MEMBERS_SCRAP:
                    break  # Stop processing if 50 members are collected
                
                try:
                    driver.execute_script("window.scrollBy(0, window.innerHeight * 0.5);")
                    sleep(5)
                    mem = all_members[i]
                    # Find the member's name
                    
                    member_name_element = mem.find_elements(By.XPATH, './/*[@class = "x78zum5 xdt5ytf xz62fqu x16ldp7u"]/div/span/span/span/a')
                    for j in range(3, len(member_name_element)):
                        
                        member = member_name_element[j]
                        member_name = member.text
                        print("member_name : ", member_name)

                        if member_name in processed_members:
                            continue  # Skip if this member has already been processed

                        processed_members.add(member_name)
                        sleep(4)
                        
                        # Scroll into view
                        scroll_into_view(driver, member)
                        
                        # Click the member name with retry
                        if not click_with_retry(driver, member):
                            continue

                        sleep(5)  # Wait for the profile to open
                        name = wait_for_element(driver, By.XPATH, '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[3]/div[2]/div[1]/div[1]/div[2]/div/div/div/div[3]/div/div/div/div[1]/div/div/div/div/div/span').text
                        print("Name:", name)
                        view_profile = wait_for_element(driver, By.XPATH, '//span[text()="View profile"]')
                        view_profile.click()
                        sleep(4)
                        about_link = wait_for_element(driver, By.XPATH, '//a[.//span[text()="About"]]')
                        about_link.click()
                        sleep(4)
                        driver.execute_script("window.scrollBy(0, window.innerHeight * 0.4);")
                        sleep(4)
                        contact_info_link = wait_for_element(driver, By.XPATH, '//a[contains(@href, "about_contact_and_basic_info")]')
                        contact_info_link.click()
                        sleep(5)
                        scrap_contact_info = wait_for_element(driver, By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div')
                        scrap_contact_info_text = scrap_contact_info.text
                        formatted_contact_text = scrap_contact_info_text.replace('\n', '\n')
                        print(f"Contact Info :\n{formatted_contact_text}")

                        # Save the data to member_list
                        member_list.append({
                            "Member Name": name,
                            "Contact Info": formatted_contact_text
                        })

                        # Navigate back to the members list
                        driver.get("https://www.facebook.com/groups/njcontractorsconnect/members")
                        sleep(3)  # Allow time for the page to load and update
                        driver.execute_script("window.scrollBy(0, window.innerHeight * 0.9);")
                        sleep(3)
                        
                        # Refetch the list of members to ensure it's up-to-date
                        all_members = wait_for_elements(driver, By.XPATH, '//*[@class="html-div x11i5rnm x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1oo3vh0 x1rdy4ex"]')
                        
                    print("member data stored: ", len(member_list))
                except StaleElementReferenceException:
                    print("Stale element reference encountered. Re-fetching the list.")
                    driver.get("https://www.facebook.com/groups/njcontractorsconnect/members")
                    sleep(3)
                    driver.execute_script("window.scrollBy(0, window.innerHeight * 0.9);")
                    sleep(3)
                except NoSuchElementException:
                    print("Element not found. Continuing with the next iteration.")
                    continue
        except Exception as e:
            print("Error occurred:", e)
            break  # Exit loop on exception to avoid getting stuck

    # Write the collected data to a CSV file
    with open('facebook_members_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Member Name', 'Contact Info']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for member in member_list:
            writer.writerow(member)

    print("Member list saved to facebook_members1.csv")
    driver.quit()

scrape_facebook_data()

# Load the CSV file into a DataFrame
df = pd.read_csv("facebook_members_data.csv")

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
final_csv = 'final_facebook_memeber_data.csv'

# Save the DataFrame to a new CSV file
df.to_csv(final_csv, index=False)
os.remove('facebook_members_data.csv')

print(f"Data extraction complete. Updated file saved as {final_csv}.")
