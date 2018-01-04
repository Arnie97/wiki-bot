#!/usr/bin/env python3

'''Reroute backlinks of a disambiguation page to the appropriate article.

Usage: {0} <disambig-page> <edit-summary> [minor]
Example: {0} CRH "Disambiguation" m
'''

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
        self.disambig_page = self.site.pages[title]
        variants = self._variants(self.disambig_page)
        self.regex = '|'.join(map(re.escape, variants))

        if self.disambig_page.page_title != variants[-1]:
            self.disambig_page = self.site.pages[variants[-1]]
        self._reset_links()

        for page in self.disambig_page.backlinks(filterredir='nonredirects'):
            self._menu_main(page)

        self._show_stat()

    def _menu_main(self, page, silent=False):
        'Show the main menu.'
        silent or self._info(page, end='\n\n')
        silent or self._print_options(
            *enumerate(self.links),
            ('-', 'Remove links'),
            ('e', 'Edit link options'),
            ('q', 'Quit'),
        )
        choice = input('--> ').strip().lower()
        if choice == '-':
            return self._replace(page, self.regex, None, raw=True)
        elif choice == 'e':
            self._menu_edit_mode()
            return self._menu_main(page)
        elif choice == 'q':
            raise KeyboardInterrupt
        try:
            n = int(choice)
            assert n != 0
            correct_link = self.links[n]
        except (ValueError, IndexError):
            self._invalid(choice)
            return self._menu_main(page, silent=True)
        except AssertionError:
            self.ignored += 1
            return
        else:
            return self._replace(page, self.regex, correct_link, raw=True)

    def _menu_edit_mode(self, silent=False):
        'Show the link editing mode submenu.'
        silent or self._print_options(
            ('i', 'Insert'),
            ('a', 'Append'),
            ('d', 'Delete'),
            ('s', 'Substitute'),
            ('r', 'Reset'),
            ('q', 'Back'),
        )
        choice = input('e > ').strip().lower()
        if choice == 'r':
            print('Resetting to default...', end=' ')
            self._reset_links()
            print('Done.')
            return
        elif choice == 'q':
            return
        elif choice in 'iadsr':
            return self._menu_edit_position(choice)
        else:
            self._invalid(choice)
            return self._menu_edit_mode(silent=True)

    def _menu_edit_position(self, mode, silent=False):
        'Show the link editing position submenu.'
        silent or self._print_options(
            *enumerate(self.links),
            ('q', 'Back'),
        )
        choice = input(mode + ' > ').strip().lower()
        if choice == 'q':
            return
        try:
            n = int(choice)
            assert mode != 'd' or n != 0
            self.links[n]
        except (ValueError, IndexError, AssertionError):
            self._invalid(choice)
            return self._menu_edit_position(mode, silent=True)
        else:
            self._edit_links(mode, n)
            return self._menu_edit_position(mode)

    def _edit_links(self, mode, n):
        'Edit link items in the option list.'
        if mode == 'd':
            self.links.pop(n)
            return

        s = input(mode + str(n) + ' > ').strip()
        if mode == 's':
            self.links[n] = s
        else:
            n += 1 if mode == 'a' else 0
            self.links.insert(n, s)

    def _reset_links(self):
        'List links in the disambiguation page.'
        contents = self.disambig_page.text()
        self.links = re.findall(self.first_link_in_line, contents)
        self.links.insert(0, self.disambig_page.page_title + '?')

    def _print_options(self, *pairs):
        'Print multiple option items in the menu.'
        for key, option in pairs:
            self._print_option(key, option)

    @staticmethod
    def _print_option(key, option):
        'Print a single option item in the menu.'
        F = colorama.Fore
        print('{F.YELLOW}[{key}]{F.RESET} {option}'.format(**locals()))


if __name__ == '__main__':
    main(Disambiguator, argc=3)
