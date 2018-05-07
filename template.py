#!/usr/bin/env python3

f = open("foo.html", 'w')
f.write("<!DOCTYPE html>\n")
f.write("<html>\n")
f.write("<head>\n")
f.write("<title>Page Title</title>\n")
f.write("</head>\n")
f.write("<body>\n")
f.write("<h1>This is a Heading</h1>\n")
f.write("<p>This is a paragraph.<p>\n")
f.write("</body>\n")
f.write("</html>\n")
f.close()
