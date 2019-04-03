#!/usr/bin/env python3

import feedparser
import os
import requests
import time

from lxml import etree, html
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from steins_web import *

class SteinsHandler:
    def __init__(self):
        self.signed_in = False

    def read_title(self, item_it):
        return item_it['title']

    def read_link(self, item_it):
        return item_it['link']

    def read_summary(self, item_it):
        try:
            summary = item_it['summary']

            while True:
                search_str1 = "<img"
                idx1 = summary.find(search_str1)
                if idx1 == -1:
                    break
                search_str2 = ">"
                idx2 = summary.find(search_str2, idx1)
                summary = summary[:idx1] + summary[idx2 + len(search_str2):]

            return summary
        except KeyError:
            return ""

    def read_time(self, item_it):
        try:
            item_time = item_it['published_parsed']
            item_time = time.strftime("%Y-%m-%d %H:%M:%S", item_time)
            return item_time
        except:
            pass

        try:
            item_time = item_it['published']
            item_time = time.strptime(item_time, "%m/%d/%Y %I:%M:%S %p")
            item_time = time.strftime("%Y-%m-%d %H:%M:%S", item_time)
            return item_time
        except:
            pass

        try:
            item_time = item_it['updated_parsed']
            item_time = time.strftime("%Y-%m-%d %H:%M:%S", item_time)
            return item_time
        except:
            pass

        try:
            item_time = item_it['updated']
            item_time = time.strptime(item_time, "%m/%d/%Y %I:%M:%S %p")
            item_time = time.strftime("%Y-%m-%d %H:%M:%S", item_time)
            return item_time
        except:
            pass

        raise KeyError

    def sign_in(self, filename):
        pass

    def parse(self, feed_link):
        return feedparser.parse(feed_link)

class AtlanticHandler(SteinsHandler):
    def sign_in(self, filename):
        with open(filename, 'r') as f:
            file_opened = True
            tree = etree.fromstring(f.read())
            try:
                node = tree.xpath("//atlantic")[0]
            except IndexError:
                return
        if not file_opened:
            return

        browser = get_browser()
        browser.get("https://accounts.theatlantic.com/login/")
        wait = WebDriverWait(browser, 30)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'I Accept')]")))
        button = browser.find_elements_by_xpath("//button[contains(text(), 'I Accept')]")[0]
        button.click()

        email = browser.find_element_by_name("login-email")
        email.send_keys(node.xpath("./email")[0].text)
        pwd = browser.find_element_by_name("login-password")
        pwd.send_keys(node.xpath("./password")[0].text)
        button = browser.find_element_by_name("_submit_login")
        button.click()

        wait = WebDriverWait(browser, 30)
        wait.until(EC.title_contains("Edit Profile"))
        fetch_cookies()
        self.signed_in = True

    def parse(self, feed_link):
        tree = get_tree_from_session(feed_link)
        contents = tree.xpath("//content")
        for content_it in contents:
            content_it.getparent().remove(content_it)
        d = feedparser.parse(html.tostring(tree))
        return d

class EconomistHandler(SteinsHandler):
    def sign_in(self, filename):
        with open(filename, 'r') as f:
            file_opened = True
            tree = etree.fromstring(f.read())
            try:
                node = tree.xpath("//economist")[0]
            except IndexError:
                return
        if not file_opened:
            return

        browser = get_browser()
        browser.get("https://www.economist.com")
        button = browser.find_element_by_xpath("//a[contains(@href, '/free-email-newsletter-signup?tab=login')]")
        button.click()
        button = browser.find_element_by_xpath("//button[contains(text(), 'Log In')]")
        button.click()

        email = browser.find_element_by_xpath("//input[contains(@placeholder, 'E-mail address')]")
        email.send_keys(node.xpath("./email")[0].text)
        pwd = browser.find_element_by_xpath("//input[contains(@placeholder, 'Password')]")
        pwd.send_keys(node.xpath("./password")[0].text)
        button = browser.find_element_by_id("submit-login")
        button.click()

        wait = WebDriverWait(browser, 30)
        wait.until(EC.title_contains("World News"))
        fetch_cookies()
        self.signed_in = True

class FinancialTimesHandler(SteinsHandler):
    def sign_in(self, filename):
        with open(filename, 'r') as f:
            file_opened = True
            tree = etree.fromstring(f.read())
            try:
                node = tree.xpath("//financial_times")[0]
            except IndexError:
                return
        if not file_opened:
            return

        while True:
            try:
                browser = get_browser()
                browser.get("https://accounts.ft.com/login/")
                email = browser.find_element_by_id("enter-email")
                email.send_keys(node.xpath("./email")[0].text)
                button = browser.find_element_by_id("enter-email-next")
                button.click()
                button = browser.find_element_by_id("sso-redirect-button")
                button.click()
                uid = browser.find_element_by_id("userid")
                uid.send_keys(node.xpath("./user_id")[0].text)
                pwd = browser.find_element_by_id("pwd")
                pwd.send_keys(node.xpath("./password")[0].text)
                button = browser.find_element_by_name("submit")
                button.click()
                break
            except NoSuchElementException:
                print("ERROR: FinancialTimesHandler.")

        wait = WebDriverWait(browser, 30)
        wait.until(EC.title_contains("Financial Times"))
        fetch_cookies()
        self.signed_in = True

class GuardianHandler(SteinsHandler):
    def sign_in(self, filename):
        with open(filename, 'r') as f:
            file_opened = True
            tree = etree.fromstring(f.read())
            try:
                node = tree.xpath("//guardian")[0]
            except IndexError:
                return
        if not file_opened:
            return

        browser = get_browser()
        browser.get("https://profile.theguardian.com/signin/")
        email = browser.find_element_by_id("tssf-email")
        email.send_keys(node.xpath("./email")[0].text)
        button = browser.find_element_by_id("tssf-submit")
        button.click()
        wait = WebDriverWait(browser, 30)
        wait.until(EC.element_to_be_clickable((By.ID, "tssf-sign-in")))
        pwd = browser.find_element_by_id("tsse-password")
        pwd.send_keys(node.xpath("./password")[0].text)
        button = browser.find_element_by_id("tssf-sign-in")
        button.click()

        wait = WebDriverWait(browser, 30)
        wait.until_not(EC.title_contains("Sign in"))
        fetch_cookies()
        self.signed_in = True

class MangaStreamHandler(SteinsHandler):
    def parse(self, feed_link):
        tree = get_tree_from_session(feed_link)
        titles = tree.xpath("//item/title")
        for title_it in titles:
            if not "One Piece" in title_it.text:
                item_it = title_it.getparent()
                channel_it = item_it.getparent()
                channel_it.remove(item_it)
        d = feedparser.parse(html.tostring(tree))
        return d

class NewYorkerHandler(SteinsHandler):
    def sign_in(self, filename):
        with open(filename, 'r') as f:
            file_opened = True
            tree = etree.fromstring(f.read())
            try:
                node = tree.xpath("//new_yorker")[0]
            except IndexError:
                return
        if not file_opened:
            return

        browser = get_browser()
        browser.get("https://account.newyorker.com")
        email = browser.find_element_by_id("username")
        email.send_keys(node.xpath("./email")[0].text)
        pwd = browser.find_element_by_id("userpass")
        pwd.send_keys(node.xpath("./password")[0].text)
        button = browser.find_element_by_id("signIn")
        button.click()

        wait = WebDriverWait(browser, 30)
        wait.until(EC.element_to_be_clickable((By.ID, "profileEdit")))
        fetch_cookies()
        self.signed_in = True

class WIREDHandler(SteinsHandler):
    def sign_in(self, filename):
        with open(filename, 'r') as f:
            file_opened = True
            tree = etree.fromstring(f.read())
            try:
                node = tree.xpath("//wired")[0]
            except IndexError:
                return
        if not file_opened:
            return

        browser = get_browser()
        browser.get("https://www.wired.com/account/sign-in/")
        email = browser.find_element_by_id("email-input")
        email.send_keys(node.xpath("./email")[0].text)
        pwd = browser.find_element_by_id("password-input")
        pwd.send_keys(node.xpath("./password")[0].text)
        button = browser.find_element_by_xpath("//input[contains(@value, 'Sign In')]")
        button.click()

        wait = WebDriverWait(browser, 30)
        wait.until_not(EC.title_contains("Sign in"))
        fetch_cookies()
        self.signed_in = True

# Static factory.
def get_handler(source, filename="sign_in.xml"):
    if "The Atlantic" in source:
        global atlantic_handler
        if not "atlantic_handler" in globals():
            print("DEBUG: AtlanticHandler.")
            atlantic_handler = AtlanticHandler()
        handler = atlantic_handler
    elif "Economist" in source:
        global economist_handler
        if not "economist_handler" in globals():
            print("DEBUG: EconomistHandler.")
            economist_handler = EconomistHandler()
        handler = economist_handler
    elif "Financial Times" in source:
        global financial_times_handler
        if not "financial_times_handler" in globals():
            print("DEBUG: FinancialTimesHandler.")
            financial_times_handler = FinancialTimesHandler()
        handler = financial_times_handler
    elif "The Guardian" in source:
        global guardian_handler
        if not "guardian_handler" in globals():
            print("DEBUG: GuardianHandler.")
            guardian_handler = GuardianHandler()
        handler = guardian_handler
    elif "Manga Stream" in source:
        global manga_stream_handler
        if not "manga_stream_handler" in globals():
            print("DEBUG: MangaStreamHandler.")
            manga_stream_handler = MangaStreamHandler()
        handler = manga_stream_handler
    elif "The New Yorker" in source:
        global new_yorker_handler
        if not "new_yorker_handler" in globals():
            print("DEBUG: NewYorkerHandler.")
            new_yorker_handler = NewYorkerHandler()
        handler = new_yorker_handler
    elif "WIRED" in source:
        global wired_handler
        if not "wired_handler" in globals():
            print("DEBUG: WIREDHandler.")
            wired_handler = WIREDHandler()
        handler = wired_handler
    else:
        handler = SteinsHandler()

    dir_name = os.path.dirname(os.path.abspath(__file__))
    file_name = dir_name + os.sep + filename
    if os.path.exists(file_name) and not handler.signed_in:
        handler.sign_in(file_name)
    return handler
