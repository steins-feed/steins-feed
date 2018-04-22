#!/usr/bin/env python3

import requests
from lxml import etree

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
