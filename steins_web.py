#!/usr/bin/env python3

import os
import requests

from lxml import html
from selenium import webdriver

dir_path = os.path.dirname(os.path.abspath(__file__))

def have_browser():
    if "browser" in globals():
        return True
    else:
        return False

def get_browser(interaction_mode=False):
    global browser
    if not have_browser():
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
