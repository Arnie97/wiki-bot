#!/usr/bin/env python3

'''Reroute backlinks of a disambiguation page to the appropriate article.

Usage: {0} <disambig-page> <edit-summary> [minor]
Example: {0} CRH "Disambiguation" m
'''

import sys
import re
import colorama
from bot import main
from backlink import BacklinkBot


class Disambiguator(BacklinkBot):
    pipe_link = r'(?!(?:File|Category)\:)([^\]|]+)[^\]]*'
    first_link_in_line = r'(?m)^[^\[]*?\[\[%s\]\]' % pipe_link

    def __call__(self, title, edit_summary, minor=False):

        super(BacklinkBot, self).__call__(edit_summary, minor)
        disambig = self.site.pages[title]
        contents = disambig.text()
        self.links = re.findall(self.first_link_in_line, contents)
        self.links.insert(0, title + '?')
        self.title = title

        for page in disambig.backlinks():
            if page.namespace == 0:  # articles
                self._select(page)
            else:
                self.ignored += 1

        self._show_stat()

    def _select(self, page):
        'Select an option to proceed.'
        self._info(page, end='\n\n')
        for i, link in enumerate(self.links):
            self._option(i, link)
        self._option('r', 'Remove this link')
        self._option('e', 'Edit options')
        self._option('q', 'Quit')

        while True:
            try:
                choice = input('--> ').lower()
                n = int(choice)
                assert n
                link = self.links[n]
            except (EOFError, KeyboardInterrupt):
                choice = 'q'
            except (ValueError, IndexError):
                pass
            except AssertionError:
                self.ignored += 1
                return
            else:
                return self._evaluate(page, self.title, self.links[n])

            if choice == 'q':
                self.ignored += 1
                self._show_stat()
                sys.exit()
            elif choice == 'r':
                raise NotImplementedError
            elif choice == 'e':
                raise NotImplementedError
            else:
                message = '{0.RED}Invalid operation: {0.RESET}{1}'
                print(message.format(colorama.Fore, choice))

    @staticmethod
    def _option(key, option):
        'Print an available option.'
        F = colorama.Fore
        print('{F.YELLOW}[{key}]{F.RESET} {option}'.format(**locals()))


if __name__ == '__main__':
    main(Disambiguator, argc=3)
