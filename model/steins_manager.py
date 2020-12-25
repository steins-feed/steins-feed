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

    def xpath(self, tree, pat, ns=None):
        if ns == None:
            return tree.xpath("./{}".format(pat))
        else:
            return tree.xpath("./foo:{}".format(pat), namespaces={'foo': ns})

    def parse(self, feed_link, patterns=None):
        if patterns == None:
            d = feedparser.parse(feed_link)
            try:
                status = d.status
            except AttributeError:
                status = -1
            return d, status

        if patterns['Namespace'] == None:
            tree, status = get_tree_from_session(feed_link, 'html')
        else:
            tree, status = get_tree_from_session(feed_link)
        entries = self.xpath(tree, patterns['Entry'], patterns['Namespace'])

        l = []
        for entry_it in entries:
            l_it = {}
            try:
                l_it['title'] = self.xpath(entry_it, patterns['Title'], patterns['Namespace'])[0].text
                l_it['link'] = self.xpath(entry_it, patterns['Link'], patterns['Namespace'])[0].get('href')
                s = self.xpath(entry_it, patterns['Published'], patterns['Namespace'])[0].text
                s = s.upper()
                s = s.replace(".M", "M")
                s = s.replace("M.", "M")
                l_it['published_parsed'] = time.strptime(s, patterns['Published_format'])
            except IndexError:
                continue
            try:
                l_it['summary'] = self.xpath(entry_it, patterns['Summary'], patterns['Namespace'])[0].text
            except:
                l_it['summary'] = ""
            l.append(l_it)

        return {'items': l}, status
