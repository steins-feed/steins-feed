#!/usr/bin/env python3

import os
import requests
import time

from lxml import etree, html

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

class SteinsFactory:
    def get_handler(self, title):
        if "The Atlantic" in title:
            return AtlanticHandler()
        else:
            return SteinsHandler()

def get_attr_list():
    dir_name = os.path.dirname(os.path.abspath(__file__))
    f = open(dir_name+os.sep+"steins_manager.py", 'r')
    attr_list = []
    for line in f:
        idx1 = line.find("def get_")
        if idx1 == -1:
            continue
        idx2 = line.find("(", idx1)
        if idx2 == -1:
            continue
        attr_list.append(line[idx1+8:idx2])
    f.close()
    return attr_list

def can_print(source):
    attr_list = get_attr_list()
    for attr_it in attr_list:
        if attr_it in source:
            return True
    return False

def get_WIRED(tree):
    article = tree.xpath("//article")[0]
    article_body = article.xpath("./div")[0]
    return article_body

def get_Guardian(tree):
    article = tree.xpath("//article")[0]
    article_body = article.xpath(".//div[@itemprop='articleBody']")[0]
    return article_body

def get_Atlantic(tree):
    article = tree.xpath("//article")[0]
    article_sections = article.xpath(".//section")
    article_body = []
    for section_it in article_sections:
        for elem_it in section_it:
            article_body.append(elem_it)
    return article_body

def get_Heise(tree):
    article = tree.xpath("//article")[0]
    article_body = article.xpath(".//div[@class='article-content']")[0]
    return article_body

def get_Register(tree):
    article_body = tree.xpath("//div[@id='body']")[0]
    return article_body

def add_feed(c, title, link):
    c.execute("INSERT INTO Feeds (Title, Link) VALUES (?, ?)", (title, link, ))

def delete_feed(c, title):
    c.execute("DELETE FROM Feeds WHERE Title='?'", (title, ))

def init_feeds(c):
    f = open("steins_config.xml", 'r')
    tree = etree.fromstring(f.read())
    f.close()

    feed_list = tree.xpath("//feed")
    for feed_it in feed_list:
        title = feed_it.xpath("./title")[0].text
        link = feed_it.xpath("./link")[0].text
        add_feed(c, title, link)
