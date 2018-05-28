#!/usr/bin/env python3

import requests
import weasyprint

from lxml import html

page = requests.get("https://www.wired.com/story/a-classical-math-problem-gets-pulled-into-self-driving-cars/")
tree = html.fromstring(page.content)
article = tree.xpath("//article")[0]
article_body = article.xpath("./div")[0]

f = open("scrape_js.html", 'w')
f.write("<!DOCTYPE html>\n")
f.write("<html>\n")
f.write("<head>\n")
f.write("<meta charset=\"UTF-8\">")
f.write("<title>Stein's Feed</title>\n")
f.write("</head>\n")
f.write("<body>\n")
#f.write(html.tostring(article_body).decode())
for e_it in article_body:
    if not e_it.tag == "div":
        f.write(html.tostring(e_it).decode())
        f.write('\n')
f.write("</body>\n")
f.close()

weasyprint.HTML("scrape_js.html").write_pdf("scrape_js.pdf")
