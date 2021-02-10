import datetime
import json
import random
import time
import re
import os

from selenium import webdriver
from pymongo import MongoClient
from bs4 import BeautifulSoup as BSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

db_client = MongoClient(port=27017)
db = db_client["db"]
collection = db["timeslots"]

path_to_webdriver = "driver/chromedriver_mac64"
os.chmod(path_to_webdriver, 0755)

login_url = "https://www.walgreens.com/login.jsp"
screening_url = "https://www.walgreens.com/findcare/vaccination/covid-19/location-screening"

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
    driver.implicitly_wait(5)
    num_attempts = 3
    for i in range(num_attempts):
        try:
            driver.find_element_by_id("submit_btn").click()
        except Exception as e:
            pass


def patient_screening_v2(driver):
    driver.get(screening_url)
    site_login(driver, login_again=True)
    driver.implicitly_wait(5)
    input_text = 60604

    # Input zip code to bring up questionnaire
    # search_box_selector = "inputLocation"
    num_attempts = 3
    search_box = driver.find_element_by_id("inputLocation")
    for i in range(num_attempts):
        if search_box.get_attribute("value") != input_text:
            search_box.clear()
            search_box.send_keys(input_text)
        driver.implicitly_wait(2)
        search_box.send_keys(Keys.ARROW_DOWN)
        search_box.send_keys(Keys.ENTER)
    driver.find_element_by_xpath(
        "/html/body/div[2]/div/div/section/section/section/section/section/section[1]/div/span/button").click()
    driver.implicitly_wait(5)

    # search_box_action(driver, search_box_selector, 60604)
    driver.find_element_by_xpath(
        "/html/body/div[2]/div/div/section/section/section/section/section/section[1]/div/span/button").click()
    driver.implicitly_wait(5)

    # Select age criteria
    driver.find_element_by_xpath(
        "/html/body/div[2]/div/div/section/section/section/section/section[2]/section/section/section[3]/div/form/div[2]/div/div[1]/div/div/div[2]/fieldset/div[2]/label").click()

    # Agree to terms
    driver.find_element_by_xpath(
        "/html/body/div[2]/div/div/section/section/section/section/section[2]/section/section/section[5]/ul/fieldset/li").click()

    # Continue button
    driver.find_element_by_xpath(
        "/html/body/div[2]/div/div/section/section/section/section/section[2]/section/section/section[3]/div/form/div[2]/div/div[2]").click()

    driver.implicitly_wait(10)

    # Q1: Answer No
    driver.find_element_by_xpath(
        "/html/body/div[2]/div/div/section/section/section/div/div/div/div[3]/div/form/div[2]/div/div[2]/div[1]/div/div[2]/fieldset/div[2]/label").click()

    # Q2: Answer No
    driver.find_element_by_xpath(
        "/html/body/div[2]/div/div/section/section/section/div/div/div/div[3]/div/form/div[2]/div/div[2]/div[2]/div/div[2]/fieldset/div[2]/label").click()

    # Q3: Answer No
    driver.find_element_by_xpath(
        "/html/body/div[2]/div/div/section/section/section/div/div/div/div[3]/div/form/div[2]/div/div[2]/div[3]/div/div[2]/fieldset/div[2]/label").click()

    # Q4: Answer No
    driver.find_element_by_xpath(
        "/html/body/div[2]/div/div/section/section/section/div/div/div/div[3]/div/form/div[2]/div/div[2]/div[4]/div/div[2]/fieldset/div[2]/label").click()

    # Click Next
    driver.find_element_by_xpath(
        "/html/body/div[2]/div/div/section/section/section/div/div/div/div[3]/div/form/div[2]/div/div[3]/input").click()

    driver.implicitly_wait(5)

    # Proceed to the scheduler
    driver.find_element_by_xpath("/html/body/div[2]/div/div/section/section/section/div/div/div[3]/div/a").click()

    driver.implicitly_wait(5)

    # Select First and Second Dose
    driver.find_element_by_xpath(
        "/html/body/div[2]/div/div/section/section/section/section[1]/section[3]/section/section[2]/form/section[7]/section[1]/div").click()

    # Click on Schedule Now
    driver.find_element_by_xpath(
        "/html/body/div[2]/div/div/section/section/section/section[2]/section/span/button").click()


def parse_result(html, metro):
    soup = BSoup(html, 'lxml')
    accordion = soup.select("#wag-body-main-container > section > section > section")[0]
    results = accordion.find_all('section', id=re.compile("wag-store-info-"))
    for r in results:
        for c in r.children:
            try:
                address_left = c.select("section.pull-left.address-wrapper")[0]
                store_address = address_left.select("span.pt10")[0].text
                city = address_left.select("span:nth-child(3)")[0].text
                state = address_left.select("span:nth-child(4)")[0].text
                phone_number = address_left.select("span:nth-child(7)")[0].text
                availability = c.select("div > p")[0].text
                num_slots = availability.split(" ")[0]
                day_available = availability.split(" ")[-1]
                save(dict(
                    store_address=store_address,
                    city=city,
                    state=state,
                    phone_number=phone_number,
                    num_slots=num_slots,
                    day_available=day_available,
                    metro=metro
                ))
            except Exception as e:
                print e


def search_v2(driver, zip_code):
    parse_result(driver.page_source, zip_code.get("metro"))


def search(driver):
    driver.implicitly_wait(5)
    zip_codes = get_zip_codes()
    num_attempts = 3
    for zip_code in zip_codes:
        for i in range(num_attempts):
            search_box = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "search-address")))
            while search_box.get_attribute("value") != zip_code.get("zipcode"):
                search_box.clear()
                search_box.send_keys(zip_code.get("zipcode"))
            driver.implicitly_wait(2)
            search_box.send_keys(Keys.ARROW_DOWN)
            search_box.send_keys(Keys.ENTER)
            search_box.send_keys(Keys.ENTER)
            time.sleep(10)
            parse_result(driver.page_source, zip_code.get("metro"))
            time.sleep(60)


def save(record):
    print "Record to save: ", record
    if is_new_record(record):
        record["created"] = datetime.datetime.utcnow()
        record["tweeted"] = False
        record["provider"] = "Walgreens"
        collection.insert_one(record)
        print "Record saved"
    else:
        print "Duplicate record. Not saving"


def is_new_record(record):
    count = collection.count_documents({
        "tweeted": False,
        "city": record.get("city"),
        "store_address": record.get("store_address"),
        "day_available": record.get("day_available"),
        "phone_number": record.get("phone_number"),
        "num_slots": record.get("num_slots")
    })
    return count == 0


def get_zip_codes():
    return [{
        "zipcode": "60604",
        "metro": "Chicago"
    }]


def teardown(driver):
    # Sign out
    driver.find_element_by_xpath("/html/body/header/div[1]/nav/div/div/div[4]/div").click()
    driver.find_element_by_xpath("/html/body/header/div[1]/nav/div/div/div[4]/div/ul/li[10]").click()

    driver.close()
    driver.quit()


def run():
    while True:
        driver = setup()
        site_login(driver, login_again=False)
        patient_screening_v2(driver)
        search_v2(driver, get_zip_codes()[0])
        teardown(driver)

        # Sleep for 15 minutes before repeating
        print "Sleeping..."
        time.sleep(15 * 60)


if __name__ == '__main__':
    run()
