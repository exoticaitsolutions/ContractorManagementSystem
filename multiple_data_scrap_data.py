import csv
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from time import sleep

def type_like_human(element, text):
    for character in text:
        element.send_keys(character)

def wait_for_element(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))

def wait_for_clickable_element(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))

def wait_for_elements(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((by, value)))

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
    type_like_human(username, "abhishek@exoticaitsolutions.com")
    print("Username filled successfully")

    # Enter password
    password = wait_for_element(driver, By.ID, "pass")
    ActionChains(driver).move_to_element(password).click().perform()
    type_like_human(password, "asdf123@")
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
    max_iterations = 10  # Set the maximum number of iterations

    for _ in range(max_iterations):
        try:
            # Refetch the list of members
            all_members = wait_for_elements(driver, By.XPATH, '//*[@class="html-div x11i5rnm x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1oo3vh0 x1rdy4ex"]')

            if not all_members:
                print("No members found. Exiting.")
                break

            for i in range(len(all_members)):
                try:
                    mem = all_members[i]
                    # Find the member's name
                    member_name_element = mem.find_elements(By.XPATH, './/*[@class = "x78zum5 xdt5ytf xz62fqu x16ldp7u"]/div/span/span/span/a')
                    for j in range(3, len(member_name_element)):
                        member = member_name_element[j]
                        member_name = member.text

                        if member_name in processed_members:
                            continue  # Skip if this member has already been processed

                        processed_members.add(member_name)
                        member.click()
                        sleep(5)  # Wait for the profile to open
                        name = wait_for_element(driver, By.XPATH, '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[3]/div[2]/div[1]/div[1]/div[2]/div/div/div/div[3]/div/div/div/div[1]/div/div/div/div/div/span').text
                        print("Name:", name)
                        view_profile = wait_for_element(driver, By.XPATH, '//span[text()="View profile"]')
                        view_profile.click()
                        sleep(6)
                        about_link = wait_for_element(driver, By.XPATH, '//a[.//span[text()="About"]]')
                        about_link.click()
                        sleep(4)
                        driver.execute_script("window.scrollBy(0, window.innerHeight * 0.4);")
                        sleep(8)
                        overview = wait_for_element(driver, By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div')
                        overview = overview.text
                        formatted_overview_text = overview.replace('\n', '\n')
                        print(f"Overview :\n{formatted_overview_text}")
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

                        print("------------------------------------"*5)

                        # Navigate back to the members list
                        driver.get("https://www.facebook.com/groups/njcontractorsconnect/members")
                        sleep(5)  # Allow time for the page to load and update
                        driver.execute_script("window.scrollBy(0, window.innerHeight * 0.9);")
                        sleep(5)
                        
                        # Refetch the list of members to ensure it's up-to-date
                        all_members = wait_for_elements(driver, By.XPATH, '//*[@class="html-div x11i5rnm x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1oo3vh0 x1rdy4ex"]')

                except StaleElementReferenceException:
                    print("Stale element reference encountered. Re-fetching the list.")
                    driver.get("https://www.facebook.com/groups/njcontractorsconnect/members")
                    sleep(5)
                    driver.execute_script("window.scrollBy(0, window.innerHeight * 0.9);")
                    sleep(5)
                except NoSuchElementException:
                    print("Element not found. Continuing with the next iteration.")
                    continue
        except Exception as e:
            print("Error occurred:", e)
            break  # Exit loop on exception to avoid getting stuck

    # Write the collected data to a CSV file
    with open('facebook_members.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Member Name', 'Contact Info']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for member in member_list:
            writer.writerow(member)

    print("Member list saved to facebook_members.csv")
    driver.quit()

scrape_facebook_data()
