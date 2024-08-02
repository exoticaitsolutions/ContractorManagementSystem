# import json
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from time import sleep
# import undetected_chromedriver as uc


# def type_like_human(element, text):
#     for character in text:
#         element.send_keys(character)


# def scrape_twitter_data():
#     # driver = uc.Chrome(use_subprocess=False)
#     driver = webdriver.Chrome()
#     driver.maximize_window()

#     driver.get("https://www.facebook.com/")
#     sleep(3)

#     # Enter username
#     username = driver.find_element(By.XPATH, "//input[@name='email']")
#     ActionChains(driver).move_to_element(username).click().perform()
#     type_like_human(username, "kamal.exoticait@gmail.com")
#     print("Username filled successfully")

#     # Enter password
#     password = driver.find_element(By.ID, "pass")
#     ActionChains(driver).move_to_element(password).click().perform()
#     type_like_human(password, "asdf123@")
#     print("Password filled successfully")

#     # Click login button
#     login_button = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="royal_login_button"]')
#     login_button.click()
#     sleep(3)
#     driver.get("https://www.facebook.com/groups/njcontractorsconnect")
#     sleep(10)
#     # action = ActionChains(driver)
#     # action.move_by_offset(500, 300).click().perform()
#     # sleep(6)
#     link = driver.find_element(By.CSS_SELECTOR, 'a[href="/groups/2020285764874761/members/"]')
#     link.click()
#     sleep(10)
  
#     driver.execute_script("window.scrollBy(0, window.innerHeight * 0.3);")
#     data = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div/div/div/div/div/div[2]')
#     # print("data : ", data.text)
  

#     click_on_profile = data.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div/div/div/div/div/div[2]/div[1]/div/div[2]/div/div[1]/div/div/div[2]/div[1]/div/div/div[1]/span/span[1]/span')
#     click_on_profile.click()
#     sleep(7)
#     view_profile = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[3]/div[2]/div[1]/div[1]/div[2]/div/div/div/div[4]/div/div/div[2]/div/a/div/div[1]/div[2]/span/span')
#     view_profile.click()
#     sleep(3)
#     total_height = driver.execute_script("return document.body.scrollHeight")

#     # Calculate the position to scroll to (30% of the total height)
#     scroll_position = total_height * 0.3

#     # Scroll down to the calculated position
#     driver.execute_script(f"window.scrollTo(0, {scroll_position});")
#     sleep(3) 
#     data1 = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[1]/div[2]/div/div[1]/div/div/div/div/div[2]/div[2]')
#     print("0000000000000000", data1.text)
#     sleep(10)
    


    

# scrape_twitter_data()



import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from selenium.webdriver.chrome.options import Options

# import undetected_chromedriver as uc


def type_like_human(element, text):
    for character in text:
        element.send_keys(character)


def scrape_twitter_data():
    # driver = uc.Chrome(use_subprocess=False)
    driver = webdriver.Chrome()
    driver.maximize_window()
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--start-maximized")  # Start maximized
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.facebook.com/")
    sleep(3)

    # Enter username
    username = driver.find_element(By.XPATH, "//input[@name='email']")
    ActionChains(driver).move_to_element(username).click().perform()
    type_like_human(username, "kamal.exoticait@gmail.com")
    print("Username filled successfully")

    # Enter password
    password = driver.find_element(By.ID, "pass")
    ActionChains(driver).move_to_element(password).click().perform()
    type_like_human(password, "asdf123@")
    print("Password filled successfully")

    # Click login button
    login_button = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="royal_login_button"]')
    login_button.click()
    sleep(3)
    driver.get("https://www.facebook.com/groups/njcontractorsconnect")
    sleep(10)
    # action = ActionChains(driver)
    # action.move_by_offset(500, 300).click().perform()
    # sleep(6)
    link = driver.find_element(By.CSS_SELECTOR, 'a[href="/groups/2020285764874761/members/"]')
    link.click()
    sleep(10)
  
    driver.execute_script("window.scrollBy(0, window.innerHeight * 0.3);")
    data = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div/div/div/div/div/div[2]')
    # print("data : ", data.text)
  

    click_on_profile = data.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div/div/div/div/div/div[2]/div[1]/div/div[2]/div/div[1]/div/div/div[2]/div[1]/div/div/div[1]/span/span[1]/span')
    click_on_profile.click()
    sleep(7)
    view_profile = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[3]/div[2]/div[1]/div[1]/div[2]/div/div/div/div[4]/div/div/div[2]/div/a/div/div[1]/div[2]/span/span')
    view_profile.click()
    sleep(3)
    total_height = driver.execute_script("return document.body.scrollHeight")

    # Calculate the position to scroll to (30% of the total height)
    scroll_position = total_height * 0.3

    # Scroll down to the calculated position
    driver.execute_script(f"window.scrollTo(0, {scroll_position});")
    sleep(3) 
    data1 = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[1]/div[2]/div/div[1]/div/div/div/div/div[2]/div[2]')
    print("0000000000000000", data1.text)
    sleep(10)
    


    

scrape_twitter_data()