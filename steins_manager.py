#!/usr/bin/env python3

from datetime import datetime
import feedparser
from lxml import etree, html
import time

from steins_log import get_logger
logger = get_logger()
from steins_web import get_tree_from_session

class SteinsHandler:
    def read_title(self, item_it):
        try:
            item_title = item_it['title']
            return item_title
        except KeyError:
            pass

        logger.error("No title.")
        raise KeyError

    def read_link(self, item_it):
        try:
            item_link = item_it['link']
            return item_link
        except KeyError:
            pass

        try:
            item_link = item_it['links'][0]['href']
            return item_link
        except KeyError:
            pass

        logger.error("No link for '{}'.".format(self.read_title(item_it)))
        raise KeyError

    def read_summary(self, item_it):
        return item_it['summary']

    def read_time(self, item_it):
        try:
            item_time = item_it['published_parsed']
            item_time = datetime(*item_time[:6])
            return item_time
        except (KeyError, TypeError, ValueError):
            pass

        try:
            item_time = item_it['updated_parsed']
            item_time = datetime(*item_time[:6])
            return item_time
        except (KeyError, TypeError, ValueError):
            pass

        logger.error("No time for '{}'.".format(self.read_title(item_it)))
        raise KeyError

    def parse(self, feed_link, patterns=None):
        if patterns == None:
            return feedparser.parse(feed_link)

        tree = get_tree_from_session(feed_link)
        entries = tree.xpath("//foo:{}".format(patterns['Entry']), namespaces={'foo': patterns['Namespace']})

        l = []
        for entry_it in entries:
            l_it = {}
            l_it['title'] = entry_it.xpath("./foo:{}".format(patterns['Title']), namespaces={'foo': patterns['Namespace']})[0].text
            l_it['link'] = entry_it.xpath("./foo:{}".format(patterns['Link']), namespaces={'foo': patterns['Namespace']})[0].get('href')
            l_it['published_parsed'] = time.strptime(entry_it.xpath("./foo:{}".format(patterns['Published']), namespaces={'foo': patterns['Namespace']})[0].text[:22] + "00", "%Y-%m-%dT%H:%M:%S%z")
            l_it['summary'] = entry_it.xpath("./foo:{}".format(patterns['Summary']), namespaces={'foo': patterns['Namespace']})[0].text
            l.append(l_it)

        return {'items': l}
