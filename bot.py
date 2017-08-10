#!/usr/bin/env python3

'''MediaWiki bot framework.

Usage: {0} <edit-summary> [minor]
Example: {0} "Nothing of value" m
'''

import sys
import mwclient
import colorama


class Bot:

    def __init__(self, host, *args, **kwargs):
        'Sign in with your MediaWiki account.'
        colorama.init()
        print('Logging into %s...' % host, end=' ')
        self.site = mwclient.Site(host, *args, **kwargs)
        self.site.login()
        print('Ready.')

    def __call__(self, edit_summary, minor=False):
        'Initialize the counters.'
        self.edit_summary = edit_summary
        self.minor = minor

        self.ignored = 0
        self.edited = 0

    def __next__(self):
        'Simple progress indicator.'
        self.ignored += 1
        print('.', end='')

    @staticmethod
    def _info(page, *args, sep='', **kwargs):
        'Display the title and size of a page.'
        print(
            '\n',
            colorama.Fore.CYAN, page.name,
            colorama.Fore.GREEN, ' (', page.length, ')',
            colorama.Fore.RESET, *args, sep=sep, **kwargs)

    def _convert(self, **kwargs):
        'Convert between language variants, such as zh-CN and zh-TW.'
        return self.site.get('parse', **kwargs)['parse']['displaytitle']

    def _variants(self, page):
        'List all redirect equivalents for the page.'
        # track the redirect chain to its origin
        while page:
            origin = page
            page = page.redirects_to()

        # get all incoming redirects
        redirects = origin.backlinks(filterredir='redirects')
        variants = [p.page_title for p in redirects]
        variants.append(origin.page_title)
        return variants

    def _preview(self, contents, prefix='', color=colorama.Fore.RESET):
        'Generate a summary of changes in "diff" style.'
        print(color, end='')
        for line in contents.split('\n'):
            if any(keyword in line for keyword in self.keywords):
                print(prefix, line)
        print(colorama.Fore.RESET, end='')

    def _confirm(self, *args, **kwargs):
        'Confirm the changes.'
        prompt = ''.join((
            colorama.Fore.YELLOW,
            'Replace? [Y/n/q]: ',
            colorama.Fore.RESET))

        while True:
            try:
                choice = input(prompt).lower()
            except (EOFError, KeyboardInterrupt):
                choice = 'q'

            if choice in {'yes', 'y', ''}:
                return self._save(*args, **kwargs, verbose=True)
            elif choice in {'no', 'n'}:
                self.ignored += 1
                return
            elif choice in {'quit', 'q'}:
                self.ignored += 1
                self._show_stat()
                sys.exit()
            else:
                print(
                    colorama.Fore.RED,
                    'Invalid operation: ',
                    colorama.Fore.RESET,
                    choice)

    def _save(self, page, result, verbose=False):
        'Commit changes to MediaWiki.'
        if verbose is True:
            print('Saving...', end=' ')

        page.save(result, self.edit_summary, self.minor)
        self.edited += 1

        if verbose is True:
            print('Done.')
        elif verbose:
            print(verbose, end='')

    def _show_stat(self):
        'Show the number of edited and ignored pages.'
        print(
            '\n',
            colorama.Fore.RED,
            '%d total, %d edited, %d ignored' %
                (self.edited + self.ignored, self.edited, self.ignored),
            colorama.Fore.RESET,
            sep='')


def main(bot, argc=2, argv=sys.argv, host='zh.wikipedia.org', *args, **kwargs):
    'Parse command line options.'
    if argc <= len(argv) <= argc + 1:
        b = bot(host, *args, **kwargs)
        b(*argv[1:])
    else:  # print the docstring as help message
        import __main__
        print(__main__.__doc__.format(argv[0]))


if __name__ == '__main__':
    main(Bot)
