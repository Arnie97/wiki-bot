#!/usr/bin/env python3

import sys
import html
import mwclient
import colorama

site = mwclient.Site('test.wikipedia.org', clients_useragent='Arnie97-Bot')
site.login()

for item in site.search('nice'):
    print(''.join((
        '\n',
        colorama.Fore.CYAN,
        item['title'],
        colorama.Fore.GREEN,
        ' (', str(item['size']), ')',
        colorama.Fore.RESET
    )))
    print(html.unescape(
        item['snippet']
        .replace('<span class="searchmatch">', colorama.Fore.MAGENTA)
        .replace('</span>', colorama.Fore.RESET)
    ))

    action = input(''.join((
        colorama.Fore.YELLOW,
        'Replace? [Y/n/q]: ',
        colorama.Fore.RESET
    ))).lower()
    if not action:
        action = 'y'

    {
        'n': lambda: None,
        'y': lambda: print(item),
        'q': lambda: sys.exit()
    }[action]()
