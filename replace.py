#!/usr/bin/env python3

import sys
import html
import mwclient
import colorama


class Bot:

    def __init__(
            self,
            host='zh.wikipedia.org',
            clients_useragent='Arnie97-Bot',
            **kwargs):

        colorama.init()
        print('Logging into %s...' % host, end=' ')
        self.site = mwclient.Site(
            host=host,
            clients_useragent=clients_useragent,
            **kwargs)

        self.site.login()
        print('Ready.')


class ReplaceBot(Bot):

    def __call__(self, pattern, replacement, edit_summary, minor_edit=False):
        self.pattern = pattern
        self.replacement = replacement
        self.edit_summary = edit_summary
        self.minor_edit = minor_edit

        self.ignored = 0
        self.edited = 0

        for item in self.site.search(self.pattern):
            print(
                '\n',
                colorama.Fore.CYAN,
                item['title'],
                colorama.Fore.GREEN,
                ' (', str(item['size']), ')',
                colorama.Fore.RESET,
                sep=''
            )
            print(html.unescape(
                item['snippet']
                .replace('<span class="searchmatch">', colorama.Fore.MAGENTA)
                .replace('</span>', colorama.Fore.RESET)
            ))
            self._choose_action(item['title'])

        self._show_stat()

    def _choose_action(self, *args, **kwargs):
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
                self.edited += 1
                return self._replace(*args, **kwargs)
            elif choice in {'no', 'n'}:
                self.ignored += 1
                return
            elif choice in {'quit', 'q'}:
                self.ignored += 1
                self._show_stat()
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

    def _show_stat(self):
        print(
            '\n',
            colorama.Fore.RED,
            '%d total, %d edited, %d ignored' %
                (self.edited + self.ignored, self.edited, self.ignored),
            colorama.Fore.RESET,
            sep=''
        )


def main(argv):
    try:
        assert 4 <= len(argv) <= 5
        bot = ReplaceBot()
        bot(*argv[1:])
    except AssertionError:
        print('Usage: %s <pattern> <repl> <edit-summary> [minor]' % argv[0])


if __name__ == '__main__':
    main(sys.argv)
