from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import threading
import queue
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
import time

NUMBER_OF_MEMBERS_SCRAP = 5
USERNAME = "sandeep@exoticaitsolutions.com"
PASSWORD = "asdf123@"
MAX_WORKERS = 5

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    return driver

def open_profile_in_new_tab(driver, profile_url, member_list, tab_index):
    """Open profile in a new tab and scrape data."""
    driver.execute_script(f"window.open('{profile_url}', '_blank');")
    driver.switch_to.window(driver.window_handles[tab_index])
    sleep(5)
    
    try:
         # name = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[3]/div[2]/div[1]/div[1]/div[2]/div/div/div/div[3]/div/div/div/div[1]/div/div/div/div/div/span').text
#         # print("Name:", name)
        print(f"Scraping profile data from tab {tab_index}...")
        sleep(5)
        view_profile = driver.find_element(By.XPATH, '//span[text()="View profile"]')
        view_profile.click()
        sleep(2)
        about_link = driver.find_element(By.XPATH, '//a[.//span[text()="About"]]')
        about_link.click()
        sleep(2)
        driver.execute_script("window.scrollBy(0, window.innerHeight * 0.4);")
        sleep(2)
        contact_info_link = driver.find_element(By.XPATH, '//a[contains(@href, "about_contact_and_basic_info")]')
        contact_info_link.click()
        sleep(3)
        scrap_contact_info = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div')
        scrap_contact_info_text = scrap_contact_info.text
        formatted_contact_text = scrap_contact_info_text.replace('\n', '\n')
        print(f"Contact Info :\n{formatted_contact_text}")
        member_list.append({
            "Profile URL": profile_url,
            "Contact Info": formatted_contact_text
        })
    except Exception as e:
        print(f"Error scraping profile {profile_url}: {e}")
    finally:
        driver.close()  # Close the current tab
        driver.switch_to.window(driver.window_handles[0])  # Switch back to the original tab

def login_facebook():
    driver = create_driver()
    driver.get("https://www.facebook.com/")
    sleep(5)
    
    username = driver.find_element(By.XPATH, "//input[@name='email']")
    ActionChains(driver).move_to_element(username).click().perform()
    username.send_keys(USERNAME)
    print("Username filled successfully")

    password = driver.find_element(By.ID, "pass")
    ActionChains(driver).move_to_element(password).click().perform()
    password.send_keys(PASSWORD)
    print("Password filled successfully")

    login_button = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="royal_login_button"]')
    login_button.click()
    sleep(3)
    driver.get("https://www.facebook.com/groups/njcontractorsconnect")
    sleep(4)
    return driver

def save_to_csv(data, filename):
    """Saves the collected data to a CSV file."""
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Profile URL", "Contact Info"])
        writer.writeheader()
        writer.writerows(data)
    print(f"Data saved to {filename}")

def worker(driver, profile_queue, member_list):
    """Worker thread function."""
    while not profile_queue.empty():
        profile_url, tab_index = profile_queue.get()
        open_profile_in_new_tab(driver, profile_url, member_list, tab_index)
        profile_queue.task_done()

def scrape_facebook_data():
    start_time = time.time()
    driver = login_facebook()
    link = driver.find_element(By.CSS_SELECTOR, 'a[href="/groups/2020285764874761/members/"]')
    link.click()
    
    sleep(5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.3);")
    sleep(4)

    member_list = []
    processed_members = set()
    profile_queue = queue.Queue()

    while len(processed_members) < NUMBER_OF_MEMBERS_SCRAP:
        try:
            all_members = driver.find_elements(By.XPATH, '//*[@class="html-div x11i5rnm x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1oo3vh0 x1rdy4ex"]')

            if not all_members:
                print("No members found. Exiting.")
                break

            for i in range(len(all_members)):
                if len(processed_members) >= NUMBER_OF_MEMBERS_SCRAP:
                    break

                try:
                    driver.execute_script("window.scrollBy(0, window.innerHeight * 0.5);")
                    sleep(3)
                    mem = all_members[i]
                    member_name_element = mem.find_elements(By.XPATH, './/*[@class = "x78zum5 xdt5ytf xz62fqu x16ldp7u"]/div/span/span/span/a')

                    for j in range(3, len(member_name_element)):
                        member = member_name_element[j]
                        href_value = member.get_attribute('href')
                        print("Processing member URL:", href_value)

                        if href_value in processed_members:
                            continue

                        processed_members.add(href_value)
                        tab_index = len(driver.window_handles)
                        profile_queue.put((href_value, tab_index))

                except StaleElementReferenceException:
                    print("Stale element reference encountered. Re-fetching the list.")
                    driver.get("https://www.facebook.com/groups/njcontractorsconnect/members")
                    sleep(3)
                    driver.execute_script("window.scrollBy(0, window.innerHeight * 0.9);")
                    sleep(3)
                except NoSuchElementException:
                    print("Element not found. Continuing with the next iteration.")
                    continue

            # Create worker threads
            threads = []
            for _ in range(MAX_WORKERS):
                t = threading.Thread(target=worker, args=(driver, profile_queue, member_list))
                t.start()
                threads.append(t)

            # Wait for all threads to finish
            for t in threads:
                t.join()

        except Exception as e:
            print("Error occurred:", e)
            break

    save_to_csv(member_list, 'facebook_members.csv')
    driver.quit()

# Run the scraping function
scrape_facebook_data()

