#!/usr/bin/env python
# encoding: utf-8
"""
scrape.py

Created by Ilia Lobsanov on 2008-04-12.
Copyright (c) 2008 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import re
from mechanize import Browser
from BeautifulSoup import BeautifulSoup


def main():
    br = Browser()
    br.open("http://www.ec.gc.ca/contracts-contrats/default.asp?lang=En&n=168B9233-11")
    # follow link with element text matching regular expression
    response1 = br.follow_link(text_regex=r"Reports")
    assert br.viewing_html()
    response2 = br.follow_link(text_regex=r"Quarter")
    assert br.viewing_html()
    html = response2.read();
    response2.close()
    parse(html)

def parse(html):
    soup = BeautifulSoup(html)
    tables = soup.findAll('table')
    for table in tables:
        for row in table.findAll('tr'):
            for col in row.findAll('td'):
                if repr(col).find('Vendor Name</td>') != -1:
                    print '>>>>' + repr(col)
                else:
                    pass
            


if __name__ == '__main__':
	main()

