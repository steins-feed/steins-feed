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
        summary = "<div>" + item_it['summary'] + "</div>"
        summary_tree = html.fromstring(summary)

        # Remove.
        tags = ['figure', 'img', 'iframe', 'script', 'small', 'svg']
        for tag_it in tags:
            elems = summary_tree.xpath("//{}".format(tag_it))
            for elem_it in elems:
                elem_it.drop_tree()

        # Remove leading and trailing <br>.
        for node_it in summary_tree.xpath("//div"):
            while True:
                if len(node_it) == 0:
                    break
                if node_it[0].tag == 'br':
                    node_it[0].drop_tag()
                    continue
                if node_it[-1].tag == 'br':
                    node_it[-1].drop_tag()
                    continue
                break

        # Strip.
        tags = ['strong', 'hr']
        for tag_it in tags:
            elems = summary_tree.xpath("//{}".format(tag_it))
            for elem_it in elems:
                elem_it.drop_tag()

        res = html.tostring(summary_tree).decode()
        return res[len("<div>"):-len("</div>")]

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

class AbstractHandler(SteinsHandler):
    def read_summary(self, item_it):
        summary = super().read_summary(item_it)
        summary = "<div>" + summary + "</div>"
        summary_tree = html.fromstring(summary)

        p_nodes = summary_tree.xpath("//p")
        for node_it in p_nodes[1:]:
            node_it.drop_tree()

        res = html.tostring(summary_tree).decode()
        return res[len("<div>"):-len("</div>")]

class NoAbstractHandler(SteinsHandler):
    def read_summary(self, item_it):
        return ""

class GatesHandler(SteinsHandler):
    def read_time(self, item_it):
        try:
            item_time = item_it['published']
            item_time = datetime.strptime(item_time, "%m/%d/%Y %I:%M:%S %p")
            return item_time
        except (KeyError, TypeError, ValueError):
            pass

        logger.error("No time for '{}'.".format(self.read_title(item_it)))
        raise KeyError

class MediumHandler(SteinsHandler):
    def parse(self, feed_link):
        time.sleep(1)
        return feedparser.parse(feed_link)

# Static factory.
def get_handler(feed_it):
    title = feed_it['Title']
    if "Gates" in title:
        global gates_handler
        if not "gates_handler" in globals():
            logger.debug("GatesHandler.")
            gates_handler = GatesHandler()
        handler = gates_handler
    elif "Medium" in title:
        global medium_handler
        if not "medium_handler" in globals():
            logger.debug("MediumHandler.")
            medium_handler = MediumHandler()
        handler = medium_handler
    else:
        summary = feed_it['Summary']
        if summary == 0:
            handler = NoAbstractHandler()
        elif summary == 1:
            handler = AbstractHandler()
        else:
            handler = SteinsHandler()

    return handler
