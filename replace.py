#!/usr/bin/env python3

import sys
import html
import mwclient
import colorama


class Bot:

    def __init__(self, site, **kwargs):
        print('Logging into %s ...' % site)
        self.site = mwclient.Site(site, **kwargs)
        self.site.login()
        print('Ready.')


class ReplaceBot(Bot):

    def __init__(self, site, **kwargs):
        super().__init__(site, **kwargs)

    def __call__(self, pattern, replacement):
        self.pattern = pattern
        self.replacement = replacement

        for item in self.site.search(self.pattern):
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
            self._choose_action(item)

    def _choose_action(self, item):
        prompt = ''.join((
            colorama.Fore.YELLOW,
            'Replace? [Y/n/q]: ',
            colorama.Fore.RESET
        ))
        while True:
            choice = input(prompt).lower()

            if choice in {'yes', 'y', ''}:
                return self._replace(item)
            elif choice in {'no', 'n'}:
                return
            elif choice in {'quit', 'q'}:
                sys.exit()
            else:
                print(''.join((
                    colorama.Fore.YELLOW,
                    'Invalid operation:',
                    colorama.Fore.RESET
                )))


def main(argv):
    bot = ReplaceBot('test.wikipedia.org', clients_useragent='Arnie97-Bot')
    bot('nice', None)


if __name__ == '__main__':
    main(sys.argv)
