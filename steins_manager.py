#!/usr/bin/env python3

import os
import requests
import time

from lxml import etree, html
from selenium import webdriver

# Singleton.
def get_browser():
    global browser
    if not "browser" in globals():
        print("DEBUG: Firefox.")
        dir_name = os.path.dirname(os.path.abspath(__file__))
        gecko_path = dir_name + os.sep + "geckodriver"
        options = webdriver.firefox.options.Options()
        options.add_argument('-headless')
        #browser = webdriver.Firefox()
        #browser = webdriver.Firefox(firefox_options=options)
        browser = webdriver.Firefox(executable_path=gecko_path, firefox_options=options)
    return browser

class SteinsHandler:
    def __init__(self):
        self.signed_in = False

    def read_title(self, item_it):
        return item_it['title']

    def read_link(self, item_it):
        return item_it['link']

    def read_summary(self, item_it):
        try:
            return item_it['summary']
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

    def can_print(self):
        if "get_article_body" in dir(self):
            return True
        else:
            return False

    def sign_in(self):
        pass

    def get_article_head(self, row):
        article_head = []
        article_head.append("<h1>{}</h1>".format(row[1]).encode('utf-8'))
        article_head.append("<p>{}</p>".format(row[3]).encode('utf-8'))
        article_head.append("<p>Source: {}. Published: {}</p>".format(row[4], row[2]).encode('utf-8'))
        return article_head

class AtlanticHandler(SteinsHandler):
    #def read_summary(self, item_it):
    #    item_link = self.read_link(item_it)
    #    if "/video/" in item_link:
    #        return ""
    #    if "/photo/" in item_link:
    #        return ""

    #    page = requests.get(item_link)
    #    tree = html.fromstring(page.content)
    #    nodes = tree.xpath("//p[@itemprop='description']")
    #    item_summary = nodes[0].text

    #    return item_summary

    def get_article_head(self, row):
        page = requests.get(row[5])
        tree = html.fromstring(page.content)
        article = tree.xpath("//article")[0]
        article_cover = article.xpath(".//figure[@class='c-lead-media']")[0]
        article_cover.xpath(".//picture")[0].set("style", "display: block; overflow: hidden;")
        article_cover.xpath(".//img")[0].set("style", "max-width: 100%; height:auto;")

        article_head = []
        article_head.append("<h1>{}</h1>".format(row[1]).encode('utf-8'))
        article_head.append("<p>{}</p>".format(row[3]).encode('utf-8'))
        article_head.append(html.tostring(article_cover))
        article_head.append("<p>Source: {}. Published: {}</p>".format(row[4], row[2]).encode('utf-8'))

        return article_head

    def get_article_body(self, link):
        page = requests.get(link)
        tree = html.fromstring(page.content)
        article = tree.xpath("//article")[0]
        article_sections = article.xpath(".//section[@itemprop='articleBody']")

        article_body = []
        for section_it in article_sections:
            for elem_it in section_it:
                can_print = False
                can_print |= (elem_it.tag == "p")
                can_print |= (elem_it.tag == "figure")
                for i in range(6):
                    can_print |= (elem_it.tag == "h{}".format(i+1))
                can_print |= (elem_it.tag == "blockquote")

                if can_print:
                    elem_str = html.tostring(elem_it).decode()
                    if elem_it.tag == "figure":
                        elem_str = elem_str.replace("data-srcset", "srcset")
                    article_body.append(elem_str.encode())

        return article_body

class WIREDHandler(SteinsHandler):
    def get_article_body(self, link):
        page = requests.get(link)
        tree = html.fromstring(page.content)
        article = tree.xpath("//article")[0]
        article_body_temp = article.xpath("./div")[0]
        if article_body_temp[0].tag == "section":
            article_body_temp_new = []
            for section_it in article_body_temp:
                article_body_temp_new += section_it
            article_body_temp = article_body_temp_new

        article_body = []
        for elem_it in article_body_temp:
            can_print = False
            can_print |= (elem_it.tag == "p")
            for i in range(6):
                can_print |= (elem_it.tag == "h{}".format(i+1))
            can_print |= (elem_it.tag == "blockquote")

            if can_print:
                article_body.append(html.tostring(elem_it))

        return article_body

class GuardianHandler(SteinsHandler):
    def get_article_body(self, link):
        page = requests.get(link)
        tree = html.fromstring(page.content)
        article = tree.xpath("//article")[0]
        article_body_temp = article.xpath(".//div[@itemprop='articleBody']")[0]

        article_body = []
        for elem_it in article_body_temp:
            can_print = False
            can_print |= (elem_it.tag == "p")
            for i in range(6):
                can_print |= (elem_it.tag == "h{}".format(i+1))
            can_print |= (elem_it.tag == "blockquote")

            if can_print:
                article_body.append(html.tostring(elem_it))

        return article_body

class FinancialTimesHandler(SteinsHandler):
    def get_article_body(self, link):
        browser = get_browser()
        browser.get(link)
        tree = html.fromstring(browser.page_source)
        article = tree.xpath("//article")[0]
        article_body_temp = article.xpath(".//div[@data-trackable='article-body']")[0]

        article_body = []
        for elem_it in article_body_temp:
            can_print = False
            can_print |= (elem_it.tag == "p")
            for i in range(6):
                can_print |= (elem_it.tag == "h{}".format(i+1))
            can_print |= (elem_it.tag == "blockquote")

            if can_print:
                article_body.append(html.tostring(elem_it))

        return article_body

    def sign_in(self):
        dir_name = os.path.dirname(os.path.abspath(__file__))
        f = open(dir_name + os.sep + "sign_in.xml", 'r')
        tree = etree.fromstring(f.read())
        node = tree.xpath("//financial_times")[0]
        f.close()

        browser = get_browser()
        browser.get("https://accounts.ft.com/login")
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

        self.signed_in = True

#class HeiseHandler(SteinsHandler):
#    def get_article_body(self, tree):
#        article = tree.xpath("//article")[0]
#        article_sections = article.xpath(".//div[@class='article-content']")[0]
#
#        article_body = []
#        for section_it in article_sections:
#            for elem_it in section_it:
#                can_print = False
#                can_print |= (elem_it.tag == "p")
#                for i in range(6):
#                    can_print |= (elem_it.tag == "h{}".format(i+1))
#                can_print |= (elem_it.tag == "blockquote")
#
#                if can_print:
#                    article_body.append(elem_it)
#
#        return article_body

#class RegisterHandler(SteinsHandler):
#    def get_article_body(self, tree):
#        article_sections = tree.xpath("//div[@id='body']")[0]
#
#        article_body = []
#        for section_it in article_sections:
#            for elem_it in section_it:
#                can_print = False
#                can_print |= (elem_it.tag == "p")
#                for i in range(6):
#                    can_print |= (elem_it.tag == "h{}".format(i+1))
#                can_print |= (elem_it.tag == "blockquote")
#
#                if can_print:
#                    article_body.append(elem_it)
#
#        return article_body

# Static factory.
def get_handler(source):
    if "The Atlantic" in source:
        global atlantic_handler
        if not "atlantic_handler" in globals():
            print("DEBUG: AtlanticHandler.")
            atlantic_handler = AtlanticHandler()
        handler = atlantic_handler
    elif "WIRED" in source:
        global wired_handler
        if not "wired_handler" in globals():
            print("DEBUG: WIREDHandler.")
            wired_handler = WIREDHandler()
        handler = wired_handler
    elif "The Guardian" in source:
        global guardian_handler
        if not "guardian_handler" in globals():
            print("DEBUG: GuardianHandler.")
            guardian_handler = GuardianHandler()
        handler = guardian_handler
    elif "Financial Times" in source:
        global financial_times_handler
        if not "financial_times_handler" in globals():
            print("DEBUG: FinancialTimesHandler.")
            financial_times_handler = FinancialTimesHandler()
        handler = financial_times_handler
    #elif "Heise" in source:
    #    handler = HeiseHandler()
    #elif "The Register" in source:
    #    handler = RegisterHandler()
    else:
        handler = SteinsHandler()

    if not handler.signed_in:
        handler.sign_in()
    return handler
