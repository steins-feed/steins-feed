#!/usr/bin/env python3

import feedparser
import time

from lxml import html
from lxml.etree import ParserError

from steins_log import get_logger
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
        try:
            summary_tree = html.fromstring(item_it['summary'])

            if summary_tree.tag == "img":
                return ""
            image_nodes = summary_tree.xpath("//img")
            for node_it in image_nodes:
                node_it.getparent().remove(node_it)

            return html.tostring(summary_tree).decode('utf-8')
        except:
            get_logger().error("No summary for '{}'.".format(self.read_title(item_it)))
            return ""

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
        try:
            summary_tree = html.fromstring(item_it['summary'])
            p_nodes = summary_tree.xpath("//p")
            return html.tostring(p_nodes[0]).decode('utf-8')
        except:
            get_logger().error("No summary for '{}'.".format(self.read_title(item_it)))
            return ""

class NoAbstractHandler(SteinsHandler):
    def read_summary(self, item_it):
        return ""

class AtlanticHandler(SteinsHandler):
    def parse(self, feed_link):
        tree = get_tree_from_session(feed_link)
        contents = tree.xpath("//content")
        for content_it in contents:
            content_it.getparent().remove(content_it)
        d = feedparser.parse(html.tostring(tree))
        return d

class MediumHandler(SteinsHandler):
    def parse(self, feed_link):
        time.sleep(1)
        return feedparser.parse(feed_link)

# Static factory.
def get_handler(source):
    logger = get_logger()

    if "The Atlantic" in source:
        global atlantic_handler
        if not "atlantic_handler" in globals():
            logger.debug("AtlanticHandler.")
            atlantic_handler = AtlanticHandler()
        handler = atlantic_handler
    elif "Bild" in source:
        global bild_handler
        if not "bild_handler" in globals():
            logger.debug("BildHandler.")
            bild_handler = NoAbstractHandler()
        handler = bild_handler
    elif "The Conversation" in source:
        global conversation_handler
        if not "conversation_handler" in globals():
            logger.debug("ConversationHandler.")
            conversation_handler = NoAbstractHandler()
        handler = conversation_handler
    elif "Factorio" in source:
        global factorio_handler
        if not "factorio_handler" in globals():
            logger.debug("FactorioHandler.")
            factorio_handler = NoAbstractHandler()
        handler = factorio_handler
    elif "Fast Company" in source:
        global fast_company_handler
        if not "fast_company_handler" in globals():
            logger.debug("FastCompanyHandler.")
            fast_company_handler = NoAbstractHandler()
        handler = fast_company_handler
    elif "Medium" in source:
        global medium_handler
        if not "medium_handler" in globals():
            logger.debug("MediumHandler.")
            medium_handler = MediumHandler()
        handler = medium_handler
    elif "New Republic" in source:
        global new_republic_handler
        if not "new_republic_handler" in globals():
            logger.debug("NewRepublicHandler.")
            new_republic_handler = NoAbstractHandler()
        handler = new_republic_handler
    elif "New Statesman" in source:
        global new_statesman_handler
        if not "new_statesman_handler" in globals():
            logger.debug("NewStatesmanHandler.")
            new_statesman_handler = AbstractHandler()
        handler = new_statesman_handler
    elif "The Ringer" in source:
        global ringer_handler
        if not "ringer_handler" in globals():
            logger.debug("RingerHandler.")
            ringer_handler = AbstractHandler()
        handler = ringer_handler
    elif source == "The Verge":
        handler = SteinsHandler()
    elif "The Verge" in source:
        global verge_handler
        if not "verge_handler" in globals():
            logger.debug("VergeHandler.")
            verge_handler = NoAbstractHandler()
        handler = verge_handler
    elif "Vox" in source:
        global vox_handler
        if not "vox_handler" in globals():
            logger.debug("VoxHandler.")
            vox_handler = AbstractHandler()
        handler = vox_handler
    else:
        handler = SteinsHandler()

    return handler
