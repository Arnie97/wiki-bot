#!/usr/bin/env python3

import mwclient

site = mwclient.Site('test.wikipedia.org', clients_useragent='Arnie97-Bot')
site.login()

for item in site.search('nice'):
    print(item['title'], item['size'])
    print(item['snippet'])
