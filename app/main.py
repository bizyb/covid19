import json
import random
import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

path_to_webdriver = "driver/chromedriver_mac64"
os.chmod(path_to_webdriver, 0755)

login_url = "https://www.walgreens.com/login.jsp"
screening_url = "https://www.walgreens.com/findcare/vaccination/covid-19/appointment/screening"
timeslot_url = "https://www.walgreens.com/hcschedulersvc/svc/v2/immunizationLocations/timeslots"

data = None
with open("zips_by_town.json", "r") as f:
    data = json.load(f)


def setup():
    return webdriver.Chrome(path_to_webdriver)


def site_login(driver, login_again=False):
    if not login_again:
        driver.get(login_url)
    driver.find_element_by_id("user_name").send_keys("bizm2021@gmail.com")
    driver.find_element_by_id("user_password").send_keys("moon-age-dream-22")
    driver.find_element_by_id("submit_btn").click()


def patient_screening(driver):
    driver.get(screening_url)
    site_login(driver, login_again=True)

    # Wait for the page to load
    # Fill out the check boxes
    driver.implicitly_wait(30)
    driver.find_element_by_xpath(
        "/html/body/div[2]/div/div/section/section/section/div/div/div/div[3]/div/form/div[2]/div/div[2]/div[2]/div/div[2]/fieldset/div[1]/label").click()
    driver.find_element_by_xpath(
        "/html/body/div[2]/div/div/section/section/section/div/div/div/div[3]/div/form/div[2]/div/div[2]/div[3]/div/div[2]/fieldset/div[2]/label").click()
    driver.find_element_by_xpath(
        "/html/body/div[2]/div/div/section/section/section/div/div/div/div[3]/div/form/div[2]/div/div[2]/div[4]/div/div[2]/fieldset/div[2]/label").click()
    driver.find_element_by_xpath(
        "/html/body/div[2]/div/div/section/section/section/div/div/div/div[3]/div/form/div[2]/div/div[2]/div[5]/div/div[2]/fieldset/div[2]/label").click()
    driver.find_element_by_xpath(
        "/html/body/div[2]/div/div/section/section/section/div/div/div/div[3]/div/form/div[2]/div/div[2]/div[6]/div/div[2]/fieldset/div[2]/label").click()

    # Submit answers to the screening
    driver.implicitly_wait(15)
    driver.find_element_by_xpath(
        "/html/body/div[2]/div/div/section/section/section/div/div/div/div[3]/div/form/div[2]/div/div[3]/input").click()

    # Wait for page to load and click on the button to proceed to the scheduler
    driver.implicitly_wait(15)
    driver.find_element_by_xpath("/html/body/div[2]/div/div/section/section/section/div/div/div[3]/div/a").click()
    driver.find_element_by_xpath(
        "/html/body/div[2]/div/div/section/section/section/section[1]/section[3]/section/section[2]/form/section[7]/section[1]/div").click()
    driver.implicitly_wait(15)
    driver.find_element_by_xpath(
        "/html/body/div[2]/div/div/section/section/section/section[2]/section/span/button").click()


def search(driver):
    max_result_count = 10
    loading_msg = "Checking available appointments"
    result_x_path = "/html/body/div[2]/div/div/section/section/section/section/section/p[1]"
    search_btn_x_path = "/html/body/div[2]/div/div/section/section/section/section/div[1]/a/span"
    result_list_x_path = "/html/body/div[2]/div/div/section/section/section/section/section"
    result_item_x_path = "wag-store-info-{}"
    driver.implicitly_wait(5)

    # zip_codes = get_zip_codes()
    # /html/body/div[5]
    zip_codes = ["02139", "60645"]
    while True:
        for zip_code in zip_codes:
            search_box = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "search-address")))
            while search_box.get_attribute("value") != zip_code:
                search_box.clear()
                search_box.send_keys(zip_code)
            driver.implicitly_wait(2)
            search_box.send_keys(Keys.ARROW_DOWN)
            search_box.send_keys(Keys.ENTER)

            # driver.find_element_by_xpath(search_btn_x_path).click()
            # autocomplete = WebDriverWait(driver, 10).until(
            #     EC.visibility_of_element_located((By.CLASS_NAME, "pac-item")))
            # autocomplete.click()

            # driver.find_element_by_xpath(search_btn_x_path).click()
            # driver.execute_script("arguments[0].value = '{}';".format(zip_code), search_box)
            # driver.find_element_by_xpath(search_btn_x_path).click()
            # driver.implicitly_wait(5)
            # results = driver.find_element_by_xpath(result_list_x_path)
            # result_item = results.find_element_by_id(result_item_x_path.format(0)).text
            # print result_item
            time.sleep(10)


        # for i in range(max_result_count):
        #     results = driver.find_element_by_xpath(result_list_x_path)
        #     print results
        #     result_item = results.find_element_by_id(result_item_x_path.format(i)).text
        #     print "--------------------------------------"
        #     print result_item



def get_zip_codes():
    zip_codes = [
        "60645",  # Chicago
        "60202",  # Evanston
        "60076",  # Skokie
        "60007",  # Schaumburg
        "60632",  # Cicero
        "61016",  # Rockford
        "62629",  # Springfield
    ]
    random.shuffle(zip_codes)
    return zip_codes

def tweet(p1, p2):
    print "Text inside of tweet(): {}, {}".format(p1, p2)


def teardown(driver):
    # todo: sign out of the account first
    driver.close()
    driver.quit()



def run():
    while True:
        driver = setup()
        site_login(driver, login_again=False)
        patient_screening(driver)
        search(driver)
        teardown(driver)

        # Sleep for 30 minutes before repeating
        time.sleep(30*60)

if __name__ == '__main__':
    run()
