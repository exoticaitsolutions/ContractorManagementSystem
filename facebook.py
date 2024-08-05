import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def type_like_human(element, text):
    for character in text:
        element.send_keys(character)

def wait_for_element(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))

def scrape_facebook_data():
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--start-maximized")  # Start maximized
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    driver.get("https://www.facebook.com/")
    sleep(3)

    # Enter username
    username = wait_for_element(driver, By.XPATH, "//input[@name='email']")
    ActionChains(driver).move_to_element(username).click().perform()
    type_like_human(username, "Germniyn Williams")
    print("Username filled successfully")

    # Enter password
    password = wait_for_element(driver, By.ID, "pass")
    ActionChains(driver).move_to_element(password).click().perform()
    type_like_human(password, "S5Us3/)pT$.H#yy")
    print("Password filled successfully")

    # Click login button
    login_button = wait_for_element(driver, By.CSS_SELECTOR, 'button[data-testid="royal_login_button"]')
    login_button.click()
    sleep(3)
    driver.get("https://www.facebook.com/groups/njcontractorsconnect")
    sleep(4)

    link = wait_for_element(driver, By.CSS_SELECTOR, 'a[href="/groups/2020285764874761/members/"]')
    link.click()
    sleep(5)

    while True:
        try:
            # Scroll down to load more members if necessary
            driver.execute_script("window.scrollBy(0, window.innerHeight * 0.9);")
            sleep(5)

            # Re-find members element and list
            all_members = wait_for_element(driver, By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div/div/div/div/div/div[2]/div[4]/div/div[2]/div')
            members = all_members.find_elements(By.CLASS_NAME, 'xt0psk2')
            print("Number of members found:", len(members))

            if not members:
                print("No more members found. Exiting...")
                break

            for i, member in enumerate(members):
                try:
                    print(f"Clicking on member {i+1}")
                    member.click()
                    sleep(5)

                    # Scrape data
                    name = wait_for_element(driver, By.XPATH, '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[3]/div[2]/div[1]/div[1]/div[2]/div/div/div/div[3]/div/div/div/div[1]/div/div/div/div/div/span').text
                    print("Name:", name)

                    view_profile = wait_for_element(driver, By.XPATH, '//span[text()="View profile"]')
                    view_profile.click()
                    sleep(6)

                    about_link = wait_for_element(driver, By.XPATH, '//a[.//span[text()="About"]]')
                    about_link.click()
                    sleep(4)

                    driver.execute_script("window.scrollBy(0, window.innerHeight * 0.5);")
                    sleep(8)

                    overview = wait_for_element(driver, By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div')
                    print("Overview:", overview.text)

                    work_and_education_link = wait_for_element(driver, By.XPATH, '//a[contains(@href, "about_work_and_education")]')
                    work_and_education_link.click()
                    sleep(5)
                    scrap_work_and_education_data = wait_for_element(driver, By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div')
                    print("Work and Education Data:", scrap_work_and_education_data.text)

                    places_lived_link = wait_for_element(driver, By.XPATH, '//a[contains(@href, "about_places")]')
                    places_lived_link.click()
                    sleep(5)
                    scrap_places_lived = wait_for_element(driver, By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div')
                    print("Places Lived:", scrap_places_lived.text)

                    contact_info_link = wait_for_element(driver, By.XPATH, '//a[contains(@href, "about_contact_and_basic_info")]')
                    contact_info_link.click()
                    sleep(5)
                    scrap_contact_info = wait_for_element(driver, By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div')
                    print("Contact Info:", scrap_contact_info.text)

                    family_relationships_link = wait_for_element(driver, By.XPATH, '//a[contains(@href, "about_family_and_relationships")]')
                    family_relationships_link.click()
                    sleep(5)
                    scrap_family_relationships = wait_for_element(driver, By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div')
                    print("Family Relationships:", scrap_family_relationships.text)

                    details_about_zultan_link = wait_for_element(driver, By.XPATH, '//a[contains(@href, "about_details")]')
                    details_about_zultan_link.click()
                    sleep(5)
                    scrap_details_about = wait_for_element(driver, By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div')
                    print("Details About:", scrap_details_about.text)

                    life_events_link = wait_for_element(driver, By.XPATH, '//a[contains(@href, "about_life_events")]')
                    life_events_link.click()
                    sleep(5)
                    scrap_life_events = wait_for_element(driver, By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]')
                    print("Life Events:", scrap_life_events.text)
                    driver.get("https://www.facebook.com/groups/njcontractorsconnect/members")
                    sleep(3)
                    driver.execute_script("window.scrollBy(0, window.innerHeight * 0.9);")
                    sleep(3)

                except Exception as e:
                    print(f"An error occurred during member data scraping: {e}")

                # Re-find the members list after navigating back
                # all_members = wait_for_element(driver, By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div/div/div/div/div/div[2]/div[4]/div/div[2]/div')
                # members = all_members.find_elements(By.CLASS_NAME, 'xt0psk2')
                # print("Refetched members:", len(members))

        except Exception as e:
            print(f"An error occurred while finding members: {e}")
            break

    driver.quit()

scrape_facebook_data()

