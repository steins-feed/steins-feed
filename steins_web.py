#!/usr/bin/env python3

import os
import requests

from lxml import html
from selenium import webdriver

def get_browser():
    global browser
    if not "browser" in globals():
        print("DEBUG: Firefox.")
        dir_name = os.path.dirname(os.path.abspath(__file__))
        gecko_path = dir_name + os.sep + "geckodriver"
        options = webdriver.firefox.options.Options()
        #options.add_argument('-headless')
        browser = webdriver.Firefox(executable_path=gecko_path, firefox_options=options)
    return browser

def get_session():
    global session
    if not "session" in globals():
        print("DEBUG: Session.")
        session = requests.Session()
    return session

def get_tree_from_session(item_link):
    session = get_session()
    page = session.get(item_link)
    tree = html.fromstring(page.content)
    return tree

def fetch_cookies():
    browser = get_browser()
    session = get_session()

    cookies = browser.get_cookies()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
