#!/usr/bin/env python3

import os
import requests
import time

from lxml import html

class SteinsHandler:
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

    def get_article_body(self, tree):
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
                    article_body.append(elem_it)

        return article_body

def get_WIRED(tree):
    article = tree.xpath("//article")[0]
    article_body = article.xpath("./div")[0]
    return article_body

def get_Guardian(tree):
    article = tree.xpath("//article")[0]
    article_body = article.xpath(".//div[@itemprop='articleBody']")[0]
    return article_body

def get_Heise(tree):
    article = tree.xpath("//article")[0]
    article_body = article.xpath(".//div[@class='article-content']")[0]
    return article_body

def get_Register(tree):
    article_body = tree.xpath("//div[@id='body']")[0]
    return article_body

class SteinsFactory:
    def get_handler(self, source):
        if "The Atlantic" in source:
            return AtlanticHandler()
        else:
            return SteinsHandler()
