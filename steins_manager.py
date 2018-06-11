#!/usr/bin/env python3

import os
import requests
import time

from lxml import html
from selenium import webdriver

# Singleton.
def get_browser():
    global browser
    if browser == None:
        browser = webdriver.Firefox()
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

class AtlanticHandler(SteinsHandler):
    def read_summary(self, item_it):
        item_link = self.read_link(item_it)
        if "/video/" in item_link:
            return ""
        if "/photo/" in item_link:
            return ""

        page = requests.get(item_link)
        tree = html.fromstring(page.content)
        nodes = tree.xpath("//p[@itemprop='description']")
        item_summary = nodes[0].text

        return item_summary

    def get_article_body(self, link):
        page = requests.get(link)
        tree = html.fromstring(page.content)
        article = tree.xpath("//article")[0]
        article_sections = article.xpath(".//section")

        article_body = []
        for section_it in article_sections:
            for elem_it in section_it:
                can_print = False
                can_print |= (elem_it.tag == "p")
                for i in range(6):
                    can_print |= (elem_it.tag == "h{}".format(i+1))
                can_print |= (elem_it.tag == "blockquote")

                if can_print:
                    article_body.append(html.tostring(elem_it))

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
        page = requests.get(link)
        tree = html.fromstring(page.content)
        # DEBUG
        f = open("foo.html", 'w')
        f.write(html.tostring(tree, pretty_print=True).decode())
        f.close()
        # GUBED
        article = tree.xpath("//article")[0]
        article_body_temp = article.xpath(".//div[@data-trackable='articleBody']")[0]

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
        handler = AtlanticHandler()
    elif "WIRED" in source:
        handler = WIREDHandler()
    elif "The Guardian" in source:
        handler = GuardianHandler()
    elif "Financial Times" in source:
        handler = FinancialTimesHandler()
    #elif "Heise" in source:
    #    handler = HeiseHandler()
    #elif "The Register" in source:
    #    handler = RegisterHandler()
    else:
        handler = SteinsHandler()

    if not handler.signed_in:
        handler.sign_in()
    return handler
