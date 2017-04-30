#!/usr/bin/env python3

import sys
import html
import mwclient
import colorama


class Bot:

    def __init__(self, site, **kwargs):
        print('Logging into %s...' % site, end=' ')
        self.site = mwclient.Site(site, **kwargs)
        self.site.login()
        print('Ready.')


class ReplaceBot(Bot):

    def __init__(self, site, **kwargs):
        super().__init__(site, **kwargs)

    def __call__(self, pattern, replacement, edit_summary, minor_edit=True):
        self.pattern = pattern
        self.replacement = replacement
        self.edit_summary = edit_summary
        self.minor_edit = minor_edit

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
            self._choose_action(item['title'])

    def _choose_action(self, title):
        prompt = ''.join((
            colorama.Fore.YELLOW,
            'Replace? [Y/n/q]: ',
            colorama.Fore.RESET
        ))
        while True:
            try:
                choice = input(prompt).lower()
            except (EOFError, KeyboardInterrupt):
                choice = 'q'

            if choice in {'yes', 'y', ''}:
                return self._replace(title)
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

    def _replace(self, title):
        print('Saving...', end=' ')
        page = self.site.pages[title]
        original_text = page.text()
        replaced_text = original_text.replace(self.pattern, self.replacement)
        page.save(replaced_text, self.edit_summary, self.minor_edit)
        print('Done.')


def main(argv):
    bot = ReplaceBot('zh.wikipedia.org', clients_useragent='Arnie97-Bot')
    bot('任然', '仍然', '修正错别字')


if __name__ == '__main__':
    main(sys.argv)
