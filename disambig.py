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
        'Iterate through backlinks.'
        super(BacklinkBot, self).__call__(edit_summary, minor)
        self.title = title
        disambig = self._reset_links()

        for page in disambig.backlinks():
            self._select(page)

        self._show_stat()

    def _select(self, page):
        'Select an option to proceed.'
        self._info(page, end='\n\n')
        for i, link in enumerate(self.links):
            self._option(i, link)
        self._option('-', 'Remove this link')
        self._option('e', 'Edit link options')
        self._option('q', 'Quit')

        while True:
            try:
                choice = input('--> ').lower()
                n = int(choice)
                assert n != 0
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
            elif choice == '-':
                raise NotImplementedError
            elif choice == 'e':
                self._select_edit_mode()
                return self._select(page)
            else:
                self._invalid(choice)

    def _select_edit_mode(self):
        'Show the editing submenu.'
        self._option('i', 'Insert')
        self._option('a', 'Append')
        self._option('d', 'Delete')
        self._option('s', 'Substitute')
        self._option('r', 'Reset')
        self._option('q', 'Back')

        while True:
            choice = input('e > ').lower()
            if choice == 'q':
                return
            elif choice not in 'iadsr':
                self._invalid(choice)
                continue

            if choice == 'r':
                print('Resetting to default...', end=' ')
                self._reset_links()
                print('Done.')
            else:
                self._edit_links(choice)
            return self._select_edit_mode()

    def _reset_links(self):
        'List links in a disambiguation page.'
        disambig = self.site.pages[self.title]
        contents = disambig.text()
        self.links = re.findall(self.first_link_in_line, contents)
        self.links.insert(0, self.title + '?')
        return disambig

    def _edit_links(self, mode):
        'Edit links in the list.'
        for i, link in enumerate(self.links):
            self._option(i, link)
        self._option('q', 'Back')

        while True:
            choice = input(mode + ' > ').lower()
            if choice == 'q':
                return
            try:
                n = int(choice)
                assert mode != 'd' or n != 0
                link = self.links[n]
            except (ValueError, IndexError, AssertionError):
                self._invalid(choice)
                continue

            if mode == 'd':
                self.links.pop(n)
            else:
                s = input(mode + choice + ' > ')
                if mode == 's':
                    self.links[n] = s
                else:
                    n += 1 if mode == 'a' else 0
                    self.links.insert(n, s)
            return self._edit_links(mode)

    @staticmethod
    def _option(key, option):
        'Print an available option.'
        F = colorama.Fore
        print('{F.YELLOW}[{key}]{F.RESET} {option}'.format(**locals()))


if __name__ == '__main__':
    main(Disambiguator, argc=3)