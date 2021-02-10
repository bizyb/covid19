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
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

db_client = MongoClient(port=27017)
db = db_client["db"]
collection = db["timeslots"]

SLEEP_900 = 1*60 #15*60
SLEEP_10 = 5
SLEEP_5 = 2


login_url = "https://www.walgreens.com/login.jsp"
screening_url = "https://www.walgreens.com/findcare/vaccination/covid-19/location-screening"


def setup():
    options = Options()
    options.headless = True
    # return webdriver.Chrome(chrome_options=options)
    return webdriver.Chrome('driver/chromedriver_mac64', options=options)


def site_login(driver, login_again=False):
    print("Logging in")
    if not login_again:
        driver.get(login_url)
    time.sleep(SLEEP_5)
    driver.find_element_by_id("user_name").send_keys("bizm2021@gmail.com")
    time.sleep(SLEEP_5)
    driver.find_element_by_id("user_password").send_keys("moon-age-dream-22")
    time.sleep(SLEEP_5)
    num_attempts = 5
    for i in range(num_attempts):
        try:
            driver.find_element_by_id("submit_btn").click()
            break
        except Exception as e:
            pass


def drive_with_retries(driver, xpath):
    num_attempts = 5
    for i in range(num_attempts):
        try:
            driver.find_element_by_xpath(xpath).click()
            break
        except Exception as e:
            print(e, "Sleeping...")
            time.sleep(SLEEP_5)


def patient_screening_v2(driver):
    print("Patient Screening")
    driver.get(screening_url)
    time.sleep(SLEEP_10)
    try:
        site_login(driver, login_again=True)
    except Exception as e:
        pass
    print("Login success. Sleeping...")
    time.sleep(SLEEP_10)
    input_text = 60604

    # Input zip code to bring up questionnaire
    # search_box_selector = "inputLocation"
    num_attempts = 3
    for i in range(num_attempts):
        try:
            search_box = driver.find_element_by_xpath("/html/body/div[2]/div/div/section/section/section/section/section/section[1]/div/span/input")
            if search_box.get_attribute("value") != input_text:
                search_box.clear()
                time.sleep(SLEEP_5)
                search_box.send_keys(input_text)
                time.sleep(SLEEP_5)
            search_box.send_keys(Keys.ARROW_DOWN)
            time.sleep(SLEEP_5)
            search_box.send_keys(Keys.ENTER)
            time.sleep(SLEEP_5)
            break
        except Exception as e:
            print(e)

    print("Zip code entered")
    drive_with_retries(driver,
                       "/html/body/div[2]/div/div/section/section/section/section/section/section[1]/div/span/button")
    print("Waiting for eligibility result. Sleeping..")
    time.sleep(SLEEP_5)

    # Select age criteria
    drive_with_retries(driver,
                       "/html/body/div[2]/div/div/section/section/section/section/section[2]/section/section/section[3]/div/form/div[2]/div/div[1]/div/div/div[2]/fieldset/div[2]/label")

    time.sleep(SLEEP_5)
    # Agree to terms
    drive_with_retries(driver,
                       "/html/body/div[2]/div/div/section/section/section/section/section[2]/section/section/section[5]/ul/fieldset/li")

    time.sleep(SLEEP_5)
    # Continue button
    drive_with_retries(driver,
                       "/html/body/div[2]/div/div/section/section/section/section/section[2]/section/section/section[3]/div/form/div[2]/div/div[2]")
    print("Loading questionnaire. Sleeping...")
    time.sleep(SLEEP_10)

    # Q1: Answer No
    drive_with_retries(driver,
                       "/html/body/div[2]/div/div/section/section/section/div/div/div/div[3]/div/form/div[2]/div/div[2]/div[1]/div/div[2]/fieldset/div[2]")
    time.sleep(SLEEP_5)

    # Q2: Answer No
    drive_with_retries(driver,
                       "/html/body/div[2]/div/div/section/section/section/div/div/div/div[3]/div/form/div[2]/div/div[2]/div[2]/div/div[2]/fieldset/div[2]")
    time.sleep(SLEEP_5)

    # Q3: Answer No
    drive_with_retries(driver,
                       "/html/body/div[2]/div/div/section/section/section/div/div/div/div[3]/div/form/div[2]/div/div[2]/div[3]/div/div[2]/fieldset/div[2]")
    time.sleep(SLEEP_5)

    # Q4: Answer No
    drive_with_retries(driver,
                       "/html/body/div[2]/div/div/section/section/section/div/div/div/div[3]/div/form/div[2]/div/div[2]/div[4]/div/div[2]/fieldset/div[2]")
    time.sleep(SLEEP_5)

    # Click Next
    drive_with_retries(driver,
                       "/html/body/div[2]/div/div/section/section/section/div/div/div/div[3]/div/form/div[2]/div/div[3]/input")
    print("Questionnaire submitted. Sleeping...")
    time.sleep(SLEEP_5)

    # Proceed to the scheduler
    drive_with_retries(driver, "/html/body/div[2]/div/div/section/section/section/div/div/div[3]/div/a")
    print("Proceeding to dosage selection page. Sleeping...")
    time.sleep(SLEEP_5)

    # Select First and Second Dose
    drive_with_retries(driver,
                       "/html/body/div[2]/div/div/section/section/section/section[1]/section[3]/section/section[2]/form/section[7]/section[1]/div")
    time.sleep(SLEEP_5)

    # Click on Schedule Now
    drive_with_retries(driver, "/html/body/div[2]/div/div/section/section/section/section[2]/section/span/button")
    time.sleep(SLEEP_5)
    print("Loading time slot result page...")


def parse_result(html, metro):
    print("Parsing result page")
    soup = BSoup(html, 'lxml')
    try:
        accordion = soup.select("#wag-body-main-container > section > section > section")[0]
        results = accordion.find_all('section', id=re.compile("wag-store-info-"))
        print("Found {} results".format(len(results)))
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
                    print(e)
    except IndexError as e:
        print("IndexError - Unable to parse result page")


def search_v2(driver, zip_code):
    print("Loading result page")
    time.sleep(SLEEP_5)
    parse_result(driver.page_source, zip_code.get("metro"))


def save(record):
    print("Saving record: ", record)
    if is_new_record(record):
        record["created"] = datetime.datetime.utcnow()
        record["tweeted"] = False
        record["provider"] = "Walgreens"
        collection.insert_one(record)
        print("Record saved")
    else:
        print("Duplicate record. Not saving")


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
    print("Tearing down driver")
    # Sign out
    num_attempts = 3
    for i in range(num_attempts):
        try:
            time.sleep(SLEEP_5)
            driver.find_element_by_xpath("/html/body/header/div[1]/nav/div/div/div[4]/div").click()
            time.sleep(SLEEP_5)
            driver.find_element_by_xpath("/html/body/header/div[1]/nav/div/div/div[4]/div/ul/li[10]").click()
            time.sleep(SLEEP_5)
            break
        except Exception as e:
            print(e)
    driver.close()
    driver.quit()


def run():
    while True:
        print("*******************************************************************")
        print("Time now: {}    Driver starting...".format(time.time()))
        driver = setup()
        site_login(driver, login_again=False)
        time.sleep(SLEEP_5)
        patient_screening_v2(driver)
        time.sleep(SLEEP_5)
        search_v2(driver, get_zip_codes()[0])
        time.sleep(SLEEP_5)
        teardown(driver)

        # Sleep for 15 minutes before repeating
        print("Time now: {}    Sleeping...".format(time.time()))
        time.sleep(SLEEP_900)


if __name__ == '__main__':
    run()
