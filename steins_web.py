#!/usr/bin/env python3

import os
import requests
import sys

from lxml import etree, html
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

dir_path = os.path.dirname(os.path.abspath(__file__))

def have_browser():
    if "browser" in globals():
        return True
    else:
        return False

def get_browser(file_name='sign_in.xml', interaction_mode=False):
    global browser
    if not have_browser():
        print("DEBUG: Firefox.")
        gecko_path = dir_path + os.sep + "geckodriver"

        options = webdriver.firefox.options.Options()
        if not interaction_mode:
            options.add_argument('-headless') # DEBUG.

        profile = webdriver.FirefoxProfile()
        profile.set_preference('print.print_footerleft', "")
        profile.set_preference('print.print_footercenter', "")
        profile.set_preference('print.print_footerright', "")
        profile.set_preference('print.print_headerleft', "")
        profile.set_preference('print.print_headercenter', "")
        profile.set_preference('print.print_headerright', "")
        profile.set_preference('reader.content_width', 4)
        profile.set_preference('reader.font_size', 3)
        profile.set_preference('reader.line_height', 3)

        browser = webdriver.Firefox(executable_path=gecko_path, firefox_options=options, firefox_profile=profile)

        file_path = dir_path + os.sep + file_name
        with open(file_path, 'r') as f:
            tree = etree.fromstring(f.read())
            try:
                node = tree.xpath("//pocket")[0]
            except IndexError:
                return

        browser.get("https://getpocket.com/ff_signin")
        wait = WebDriverWait(browser, 30)
        wait.until(EC.element_to_be_clickable((By.ID, "submit-btn")))

        email = browser.find_element_by_name("email")
        email.send_keys(node.xpath("./email")[0].text)
        pwd = browser.find_element_by_id("password")
        pwd.send_keys(node.xpath("./password")[0].text)
        button = browser.find_element_by_id("submit-btn")
        button.click()

        wait = WebDriverWait(browser, 30)
        wait.until(EC.element_to_be_clickable((By.ID, "accept")))
        button = browser.find_element_by_id("accept")
        button.click()
        wait = WebDriverWait(browser, 30)
        wait.until(EC.title_contains("Pocket: My List"))

    return browser

def close_browser():
    if have_browser():
        browser = get_browser()
        browser.quit()

def have_session():
    if "session" in globals():
        return True
    else:
        return False

def get_session():
    global session
    if not have_session():
        print("DEBUG: Session.")
        session = requests.Session()
    return session

def get_tree_from_session(item_link):
    session = get_session()
    page = session.get(item_link)
    tree = html.fromstring(page.text.encode('utf-16'))
    return tree

def fetch_cookies():
    browser = get_browser()
    session = get_session()

    cookies = browser.get_cookies()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
