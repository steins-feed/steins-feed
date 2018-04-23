#!/usr/bin/env python3

import html
import requests
from lxml import etree

def read_guardian():
    # Open webpage.
    url = "https://www.theguardian.com/uk/technology/rss"
    #headers = {'User-Agent': "Firefox"}
    #page = requests.get(url, headers=headers)
    page = requests.get(url)
    tree = etree.fromstring(page.content)
    items = tree.xpath("//item")

    for item_it in items:
        title = item_it.xpath(".//title")[0].text
        link = item_it.xpath(".//link")[0].text
        describe = item_it.xpath(".//description")[0].text
        creator = item_it.xpath(".//dc:creator", namespaces=tree.nsmap)[0].text
        date = item_it.xpath(".//dc:date", namespaces=tree.nsmap)[0].text

        # Categories.
        cats = [cat_it.text for cat_it in item_it.xpath(".//category")]

        # Print.
        print("Title: {}".format(title))
        print("Creator: {}".format(creator))
        print("Date: {}".format(date))
        print("Description:")
        print(describe)
        print("Link: {}".format(link))
        print("Categories: {}".format(", ".join(cats)))

        print(79*"#")

def read_atlantic():
    # Open webpage.
    url = "https://www.theatlantic.com/feed/channel/technology/"
    #headers = {'User-Agent': "Firefox"}
    #page = requests.get(url, headers=headers)
    page = requests.get(url)
    tree = etree.fromstring(page.content)
    ns_map = {"ns": "http://www.w3.org/2005/Atom"}
    items = tree.xpath(".//ns:entry", namespaces=ns_map)

    for item_it in items:
        title = item_it.xpath(".//ns:title", namespaces=ns_map)[0].text
        link = item_it.xpath(".//ns:link", namespaces=ns_map)[0].get('href')
        describe = item_it.xpath(".//ns:summary", namespaces=ns_map)[0].text
        creator = item_it.xpath(".//ns:name", namespaces=ns_map)[0].text
        date = item_it.xpath(".//ns:published", namespaces=ns_map)[0].text

        # Categories.
        cats = ["Technology"]

        # Print.
        print("Title: {}".format(title))
        print("Creator: {}".format(creator))
        print("Date: {}".format(date))
        print("Description:")
        print(describe)
        print("Link: {}".format(link))
        print("Categories: {}".format(", ".join(cats)))

        print(79*"#")

read_guardian()
read_atlantic()
