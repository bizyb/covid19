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


def search(driver):
    # result_x_path = "/html/body/div[2]/div/div/section/section/section/section/section/p[1]"
    # search_btn_x_path = "/html/body/div[2]/div/div/section/section/section/section/div[1]/a/span"
    result_list_x_path = "/html/body/div[2]/div/div/section/section/section/section/section"
    result_item_id = "wag-store-info-{}"
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
            # for j in range(max_results):
            #     try:
            #         address_selector = "#wag-store-info-0 > div > section.pull-left.address-wrapper"
            #         num_slots_selector = "#wag-store-info-0 > div > div.main-content.inner.active > p"
                    # print "DEBUG 0"
                    # address = driver.find_element_by_xpath(result_list_x_path)\
                    #     .find_element_by_id(result_item_id.format(j))\
                    #     .find_element_by_css_selector(address_selector).text
                    # print "DEBUG 1"
                    # num_slots = driver.find_element_by_xpath(result_list_x_path)\
                    #     .find_element_by_id(result_item_id.format(j))\
                    #     .find_element_by_css_selector(num_slots_selector).text


                    # print "DEBUG 0"
                    # time.sleep(5)
                    # results = WebDriverWait(driver, 10).until(
                    #     EC.visibility_of_element_located((By.XPATH, result_list_x_path)))
                    #
                    # # results = driver.find_element_by_xpath(result_list_x_path)
                    # print "DEBUG 1"
                    # print "xpath: ", result_item_id.format(j)
                    # with open("walgreens-{}-{}.html".format(i, j), "w") as out:
                    #     out.write(driver.page_source.encode("utf-8"))
                    # item = WebDriverWait(results, 3).until(
                    #     EC.visibility_of_element_located((By.ID, result_item_id.format(j))))
                    # time.sleep(5)
                    # item = results.find_element_by_id(result_item_id.format(j))
                    # print "DEBUG 2"
                    # address = WebDriverWait(item, 3).until(
                    #     EC.visibility_of_element_located((By.CSS_SELECTOR, address_selector)))
                    # # address = item.find_element_by_css_selector("#wag-store-info-0 > div > section.pull-left.address-wrapper").text
                    # print "DEBUG 3"
                    # num_slots = WebDriverWait(item, 3).until(
                    #     EC.visibility_of_element_located((By.CSS_SELECTOR, num_slots_selector)))
                    # # num_slots = item.find_element_by_css_selector("#wag-store-info-0 > div > div.main-content.inner.active > p").text
                    #
                    # print "Address: ", address.text
                    # print "Num Slots: ", num_slots.text
                    # save(address.text, num_slots.text, zip_code.get("metro"))
                # except Exception as e:
                #     # print "Exception caught... ", e.message
                #     # print e
                #     break

            # Sleep for a minute before looking up another zipcode
            # time.sleep(60)


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
    # """Structure the parsed text and save it to the database"""
    # lines = address.split('\n')
    # if "available" in num_slots:
    #     city = None
    #     store_address = None
    #     num_slots = None
    #     phone_number = 0
    #     store_address_idx = 0
    #     phone_idx = 2
    #     city_idx = 1
    #     num_slots = num_slots.split(" ")[0]
    #     day_available = num_slots.split(" ")[-1]
    #     if phone_idx < len(lines):
    #         phone_number = lines[phone_idx]
    #     if city_idx < len(lines):
    #         city = lines[city_idx]
    #     if store_address_idx < len(lines):
    #         store_address = lines[store_address_idx]
    #     record = {}
    #     if city:
    #         record["city"] = city
    #     if store_address:
    #         record["store_address"] = store_address
    #     if num_slots:
    #         record["num_slots"] = num_slots
    #     if day_available:
    #         record["day_available"] = day_available
    #     if phone_number:
    #         record["phone_number"] = phone_number
    #     if record.get("num_slots"):
    #         record["created"] = datetime.datetime.utcnow()
    #         record["tweeted"] = False
    #         record["provider"] = "Walgreens"
    #         record["metro"] = metro
    #         if is_new_record(record):
    #             db.insert_one(record)
    #             print "New record: ", record
    #         else:
    #             print "Duplicate record. Not saving"
    # else:
    #     print "Timeslot availability unknown"


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
    zip_codes = [
        {
            "zipcode": "60604",
            "metro": "Chicago"
        },
        {
            "zipcode": "02114",
            "metro": "Boston"
        },
        # {
        #     "zipcode": "10460",
        #     "metro":  "NYC/Bronx",
        # },
        # {
        #     "zipcode": "11238",
        #     "metro":  "NYC/Brooklyn",
        # },
        # {
        #     "zipcode": "10280",
        #     "metro":  "New York, NY",
        # },
        # {
        #     "zipcode": "11360",
        #     "metro":  "NYC/Queens",
        # },
        # {
        #     "zipcode": "10310",
        #     "metro":  "NYC/Staten Island",
        # },
        {
            "zipcode": "90037",
            "metro":  "Los Angeles, CA",
        },
        {
            "zipcode": "77010",
            "metro":  "Houston, TX",
        },
        # {
        #     "zipcode": "85018",
        #     "metro":  "Phoenix, AZ",
        # },
        # {
        #     "zipcode": "19133",
        #     "metro":  "Philadelphia, PA",
        # },
        # {
        #     "zipcode": "33125",
        #     "metro":  "Miami, FL",
        # }
    ]
    # random.shuffle(zip_codes)
    # return zip_codes
    return [{
               "zipcode": "02114",
               "metro": "Boston"
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
        patient_screening(driver)
        search(driver)
        teardown(driver)

        # Sleep for 30 minutes before repeating
        time.sleep(3 * 60)


if __name__ == '__main__':
    run()
