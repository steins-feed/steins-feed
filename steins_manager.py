#!/usr/bin/env python3

import feedparser
import lxml
from lxml.etree import ParserError
import time

from steins_log import get_logger
from steins_sql import get_cursor
from steins_web import get_tree_from_session

class SteinsHandler:
    def read_title(self, item_it):
        try:
            item_title = item_it['title']
            return item_title
        except KeyError:
            pass

        get_logger().error("No title.")
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

        get_logger().error("No link for '{}'.".format(self.read_title(item_it)))
        raise KeyError

    def read_summary(self, item_it):
        summary = "<div>" + item_it['summary'] + "</div>"
        summary_tree = lxml.html.fromstring(summary)

        # Remove.
        tags = ["img", "iframe", "script", "figure"]
        for tag_it in tags:
            elems = summary_tree.xpath("//{}".format(tag_it))
            for elem_it in elems:
                elem_it.drop_tree()

        # Remove leading and trailing <br>.
        for node_it in summary_tree.xpath("//p") + summary_tree.xpath("//h1") + summary_tree.xpath("//h2"):
            while True:
                if len(node_it) == 0:
                    break
                if node_it[0].tag == "br":
                    node_it.remove(node_it[0])
                    continue
                if node_it[-1].tag == "br":
                    node_it.remove(node_it[-1])
                    continue
                break

        # Strip.
        tags = ["strong", "hr"]
        for tag_it in tags:
            elems = summary_tree.xpath("//{}".format(tag_it))
            for elem_it in elems:
                elem_it.drop_tag()

        res = lxml.html.tostring(summary_tree).decode('utf-8')
        return res[len("<div>"):-len("</div>")]

    def read_time(self, item_it):
        try:
            item_time = item_it['published_parsed']
            item_time = time.strftime("%Y-%m-%d %H:%M:%S GMT", item_time)
            return item_time
        except (KeyError, TypeError, ValueError):
            pass

        try:
            item_time = item_it['updated_parsed']
            item_time = time.strftime("%Y-%m-%d %H:%M:%S GMT", item_time)
            return item_time
        except (KeyError, TypeError, ValueError):
            pass

        get_logger().error("No time for '{}'.".format(self.read_title(item_it)))
        raise KeyError

    def parse(self, feed_link):
        return feedparser.parse(feed_link)

class AbstractHandler(SteinsHandler):
    def read_summary(self, item_it):
        summary = super().read_summary(item_it)
        summary = "<div>" + summary + "</div>"
        summary_tree = lxml.html.fromstring(summary)

        p_nodes = summary_tree.xpath("//p")
        for node_it in p_nodes[1:]:
            node_it.drop_tree()

        res = lxml.html.tostring(summary_tree).decode('utf-8')
        return res[len("<div>"):-len("</div>")]

class NoAbstractHandler(SteinsHandler):
    def read_summary(self, item_it):
        return ""

class AtlanticHandler(SteinsHandler):
    def parse(self, feed_link):
        tree = get_tree_from_session(feed_link)
        contents = tree.xpath("//content")
        for content_it in contents:
            content_it.drop_tree()
        d = feedparser.parse(lxml.html.tostring(tree))
        return d

class GatesHandler(SteinsHandler):
    def read_time(self, item_it):
        try:
            item_time = item_it['published']
            item_time = time.strptime(item_time, "%m/%d/%Y %I:%M:%S %p")
            item_time = time.strftime("%Y-%m-%d %H:%M:%S GMT", item_time)
            return item_time
        except (KeyError, TypeError, ValueError):
            pass

        get_logger().error("No time for '{}'.".format(self.read_title(item_it)))
        raise KeyError

class MediumHandler(SteinsHandler):
    def parse(self, feed_link):
        time.sleep(1)
        return feedparser.parse(feed_link)

# Static factory.
def get_handler(source):
    c = get_cursor()
    logger = get_logger()

    if "The Atlantic" in source:
        global atlantic_handler
        if not "atlantic_handler" in globals():
            logger.debug("AtlanticHandler.")
            atlantic_handler = AtlanticHandler()
        handler = atlantic_handler
    elif "Gates" in source:
        global gates_handler
        if not "gates_handler" in globals():
            logger.debug("GatesHandler.")
            gates_handler = GatesHandler()
        handler = gates_handler
    elif "Medium" in source:
        global medium_handler
        if not "medium_handler" in globals():
            logger.debug("MediumHandler.")
            medium_handler = MediumHandler()
        handler = medium_handler
    else:
        summary = c.execute("SELECT Summary FROM Feeds WHERE Title=?", (source, )).fetchone()[0]
        if summary == 0:
            handler = NoAbstractHandler()
        elif summary == 1:
            handler = AbstractHandler()
        else:
            handler = SteinsHandler()

    return handler
