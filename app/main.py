import json
import random
import time
import os
import requests
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

path_to_webdriver = "driver/chromedriver_mac64"
os.chmod(path_to_webdriver, 0755)

login_url = "https://www.walgreens.com/login.jsp"
screening_url = "https://www.walgreens.com/findcare/vaccination/covid-19/appointment/screening"

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
    towns_near_chicago = [
        "CHICAGO",
        "EVANSTONS",
        "SKOKIE",
        "NILES",
        "MORTON GROVE",
        "DES PLAINES",
        "SCHAUMBURG",
        "OAK LAWN",
        "OAK PARK",
        "CICERO"
    ]
    zips = data.get("zips")
    lookup_zips = []
    for k, v in zips.items():
        if k in towns_near_chicago:
            for zipcode in v:
                query = "{}, IL {}, USA".format(k.capitalize(), zipcode)
                lookup_zips.append(query)
    random.shuffle(lookup_zips)
    random.shuffle(lookup_zips)

    # There are about 120 zipcodes in lookup_zips in and around Chicago.
    # Search one zip code per 15 seconds (15*120 = 1800 seconds = 30 minutes)
    thread_wait = 15
    # request_cookies_browser = driver.get_cookies()
    # session = requests.Session()



    # time.sleep(thread_wait)
    loading_msg = "Checking available appointments"
    params = {
        "position": {
            "latitude": 42.0105286,
            "longitude": -87.6926257
        },
        "vaccine": {
            "productId": ""
        },
        "appointmentAvailability": {
            "startDateTime": "2021-02-05"
        },
        "radius": 100,
        "size": 25,
        "serviceId": "99"
    }
    test_params = {
        "serviceId": "99",
        "position": {
            "latitude": 42.0105286,
            "longitude": -87.6926257
        }
    }
    error = {
        "errors": [
            {
                "code": "FC_901_ValidationFailed",
                "message": ""
                           "/position should be object, "
                           "/vaccine should be object, "
                           "/appointmentAvailability should be object, "
                           "/radius should be number, "
                           "/size should be number, "
            }
        ]
    }

    error_2 = {
        """'{"errors":[{"code":"FC_901_ValidationFailed","message":" should have required property \'position\',  should have required property \'serviceId\',  should match exactly one schema in oneOf,  should match some schema in anyOf, "}]}'"""
    }
    timeslot_url = "https://www.walgreens.com/hcschedulersvc/svc/v2/immunizationLocations/timeslots"
    session = get_session(driver)


    # resp = driver.request("POST", timeslot_url, data=params)
    # session.headers.update({"content-type": "xyz"})
    # resp2 = session.post(timeslot_url, data=params)
    # session.headers.update({"content-type": "multipart/form-data"})
    # resp3 = session.post(timeslot_url, data=params)
    # print resp

    # /html/body/div[7]
    search_box = driver.find_element_by_id("search-address")
    driver.execute_script("arguments[0].value = '60645';", search_box)
    driver.find_element_by_xpath("/html/body/div[2]/div/div/section/section/section/section/div[1]/a/span").click()
    print "waiting for search box to load"
    # driver.implicitly_wait(15)
    # print "finished waiting..."
    # autocomplete = None
    # while not autocomplete:
    #     print "autocomplete not loaded"
    # while search_box.text:
    #     search_box.clear()
        # search_box.send_keys("60645")
        # driver.implicitly_wait(2)
        # try:
        #     autocomplete = driver.find_element_by_xpath("/html/body/div[5]")
        #     print "autocomplete loaded"
        #     print autocomplete.text
        #     autocomplete.send_keys(Keys.RETURN)
        # except NoSuchElementException as e:
        #     print "autocomplete element not found"
    result_x_path = "/html/body/div[2]/div/div/section/section/section/section/section/p[1]"\

    p1 = driver.find_element_by_xpath(result_x_path).text
    while p1 == loading_msg:
        print "p1 still loading"
        driver.implicitly_wait(2)
        p1 = driver.find_element_by_xpath(result_x_path).text
    print p1
    x = 1

    # driver.find_element_by_xpath("/html/body/div[2]/div/div/section/section/section/section/div[1]/a/span").click()


    # for query in lookup_zips:
    #     print "Query: {}".format(query)
    #     # driver.po
    #     # search_box = driver.find_element_by_id("search-address")
    #     # driver.implicitly_wait(driver_wait)
    #     # search_box.clear()
    #     # driver.implicitly_wait(driver_wait)
    #     # search_box.send_keys(query)
    #     # driver.find_element_by_xpath("/html/body/div[2]/div/div/section/section/section/section/div[1]/a/span").click()
    #     # p1 = driver.find_element_by_xpath("/html/body/div[2]/div/div/section/section/section/section/section/p[1]").text
    #     # while p1 == loading_msg:
    #     #     driver.implicitly_wait(driver_wait)
    #     #     p1 = driver.find_element_by_xpath("/html/body/div[2]/div/div/section/section/section/section/section/p[1]").text
    #     # print p1
    #     # # tweet(p1.text, p2.text)
    #     # time.sleep(thread_wait)
    #     # break
    #     # print(query)
    #     break


def get_session(driver):
    request_cookies_browser = driver.get_cookies()
    session = requests.Session()
    [session.cookies.set(c['name'], c['value']) for c in request_cookies_browser]
    return session

def tweet(p1, p2):
    print "Text inside of tweet(): {}, {}".format(p1, p2)


def teardown(driver):
    driver.close()
    driver.quit()



def run():
    while True:
        driver = setup()
        site_login(driver, login_again=False)
        patient_screening(driver)
        search(driver)

        # Sleep for 5 minutes before repeating
        time.sleep(5*60)
        teardown(driver)
        break


if __name__ == '__main__':
    run()
