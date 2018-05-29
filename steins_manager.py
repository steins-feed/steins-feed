#!/usr/bin/env python3

def add_feed(c, title, link):
    c.execute("INSERT INTO Feeds (Title, Link) VALUES (?, ?)", (title, link, ))

def delete_feed(c, title):
    c.execute("DELETE FROM Feeds WHERE Title='?'", (title, ))

def can_print(source):
    not_can_print = True
    not_can_print &= (source.find("WIRED") == -1)
    not_can_print &= (source.find("The Guardian") == -1)
    not_can_print &= (source.find("The Atlantic") == -1)
    return not not_can_print

def init_feeds(c):
    # The Guardian.
    add_feed(c, "The Guardian", "https://www.theguardian.com/uk/technology/rss")
    
    # The Atlantic.
    add_feed(c, "The Atlantic", "https://www.theatlantic.com/feed/channel/technology/")

    # WIRED.
    add_feed(c, "WIRED Guides", "https://www.wired.com/feed/tag/wired-guide/latest/rss")
    add_feed(c, "WIRED Business", "https://www.wired.com/feed/category/business/latest/rss")
    add_feed(c, "WIRED Culture", "https://www.wired.com/feed/category/culture/latest/rss")
    add_feed(c, "WIRED Ideas", "https://www.wired.com/feed/category/ideas/latest/rss")
    add_feed(c, "WIRED Science", "https://www.wired.com/feed/category/science/latest/rss")
    add_feed(c, "WIRED Security", "https://www.wired.com/feed/category/security/latest/rss")
    add_feed(c, "WIRED Transportation", "https://www.wired.com/feed/category/transportation/latest/rss")
    add_feed(c, "WIRED Backchannel", "https://www.wired.com/feed/category/backchannel/latest/rss")
    #add_feed(c, "WIRED Photo", "https://www.wired.com/feed/category/photo/latest/rss")
    add_feed(c, "WIRED", "https://www.wired.com/feed/rss")
    
    # XKCD.
    add_feed(c, "XKCD", "https://www.xkcd.com/rss.xml")

    # Chalkdust.
    add_feed(c, "Chalkdust", "http://chalkdustmagazine.com/feed/")

    # Gates Notes.
    add_feed(c, "Gates Notes", "https://www.gatesnotes.com/rss")

    # TED.
    add_feed(c, "TED Ideas", "https://ideas.ted.com/feed/")

    # Quanta Magazine.
    add_feed(c, "Quanta Magazine", "https://api.quantamagazine.org/feed/")

    # Scientific American.
    add_feed(c, "Scientific American", "http://rss.sciam.com/ScientificAmerican-Global")

    # The Register.
    add_feed(c, "The Register Data Centre", "https://www.theregister.co.uk/data_centre/headlines.atom")
    add_feed(c, "The Register Software", "https://www.theregister.co.uk/software/headlines.atom")
    add_feed(c, "The Register Security", "https://www.theregister.co.uk/security/headlines.atom")
    add_feed(c, "The Register Transformation", "https://www.theregister.co.uk/transformation/headlines.atom")
    add_feed(c, "The Register Devops", "https://www.theregister.co.uk/devops/headlines.atom")
    add_feed(c, "The Register Business", "https://www.theregister.co.uk/business/headlines.atom")
    add_feed(c, "The Register Personal Tech", "https://www.theregister.co.uk/personal_tech/headlines.atom")
    add_feed(c, "The Register Science", "https://www.theregister.co.uk/science/headlines.atom")
    add_feed(c, "The Register Emergent Tech", "https://www.theregister.co.uk/emergent_tech/headlines.atom")
    add_feed(c, "The Register Bootnotes", "https://www.theregister.co.uk/bootnotes/headlines.atom")
    add_feed(c, "The Register", "https://www.theregister.co.uk/headlines.atom")

    # Heise.
    add_feed(c, "Heise Developer", "https://www.heise.de/developer/rss/news-atom.xml")
    add_feed(c, "Heise Security", "https://www.heise.de/security/rss/news-atom.xml")
    add_feed(c, "Heise c't", "https://www.heise.de/ct/rss/artikel-atom.xml")
    add_feed(c, "Heise Make", "https://www.heise.de/make/rss/hardware-hacks-atom.xml")
    add_feed(c, "Heise iX", "https://www.heise.de/iX/rss/news-atom.xml")
    add_feed(c, "Heise Technology Review", "https://www.heise.de/tr/rss/news-atom.xml")
    add_feed(c, "Heise Telepolis", "https://www.heise.de/tp/rss/news-atom.xml")
    add_feed(c, "Heise TechStage", "https://www.techstage.de/rss.xml")
    add_feed(c, "Heise", "https://www.heise.de/newsticker/heise-atom.xml")

    # FiveThirtyEight.
    add_feed(c, "FiveThirtyEight", "https://fivethirtyeight.com/tag/nba/feed/")
    add_feed(c, "FiveThirtyEight NBA", "https://fivethirtyeight.com/tag/nba-playoffs/feed/")
    add_feed(c, "FiveThirtyEight NBA Playoffs", "https://fivethirtyeight.com/tag/basketball/feed/")

    # The Ringer.
    add_feed(c, "The Ringer NBA", "https://www.theringer.com/rss/nba/index.xml")
    add_feed(c, "The Ringer NBA Playoffs", "https://www.theringer.com/rss/nba-playoffs/index.xml")
