#!/usr/bin/env python3

'''MediaWiki bot framework.

Usage: {0} <edit-summary> [minor]
Example: {0} "Nothing of value" m
'''

import sys
import time
import collections
import configparser
import difflib
import functools
import mwclient
import colorama


class Bot:

    def __init__(self, host, username=None, password=None, *args, **kwargs):
        'Sign in with your MediaWiki account.'
        colorama.init()
        print('Connecting to %s...' % host, end=' ')
        self.site = mwclient.Site(host, *args, **kwargs)
        self.site.login(username, password)
        print('Ready.')

    def __call__(self, edit_summary, minor=False):
        'Initialize the counters.'
        self.edit_summary = edit_summary
        self.minor = minor

        self.ignored = 0
        self.edited = 0
        self.errors = 0

    def __next__(self):
        'Simple progress indicator.'
        self.ignored += 1
        print('.', end='')

    @staticmethod
    def _info(page, *args, sep='', **kwargs):
        'Display the title and size of a page.'
        message = '\n{0.CYAN}{1.name}{0.GREEN} ({1.length}){0.RESET}'
        print(message.format(colorama.Fore, page), *args, sep=sep, **kwargs)

    def _convert(self, **kwargs):
        'Convert between language variants, such as zh-CN and zh-TW.'
        return self.site.get('parse', **kwargs)['parse']['displaytitle']

    def _variants(self, page, **kwargs):
        'List redirect equivalents and language variants of the page.'
        print('Parsing variants...', end=' ')
        # track the redirect chain to its origin
        while page:
            origin = page
            print(page.name, end=' > ')
            page = page.redirects_to()

        # get all incoming redirects
        variants = self._dialects(origin.page_title, **kwargs)
        for redirect in origin.backlinks(filterredir='redirects'):
            variants.update(self._dialects(redirect.page_title, **kwargs))

        # move the origin to the end of list
        variants.discard(origin.page_title)
        variants = list(variants)
        variants.append(origin.page_title)

        print('Retrieved %d variants.' % len(variants))
        return variants

    def _dialects(self, title, dialects='zh-cn,zh-hk,zh-mo,zh-sg,zh-tw'):
        'List language variants of the title.'
        if not dialects:
            return {title}
        else:
            dialects = dialects.split(',')
        s = set()
        for dialect in dialects:
            s.add(self._convert(title=title, uselang=dialect))
        return s

    @staticmethod
    def _diff(x, y, **kwargs):
        'Generate a summary of changes in "diff" style.'
        colors = {
            '+': colorama.Fore.GREEN,
            '-': colorama.Fore.RED,
            '@': colorama.Fore.YELLOW,
        }
        x, y = x.splitlines(), y.splitlines()
        for line in difflib.unified_diff(x, y, lineterm='', **kwargs):
            for prefix, color in colors.items():
                if line.startswith(prefix):
                    print(color, line, colorama.Fore.RESET, sep='')
                    break
            else:
                print(line)

    def _confirm(self, *args, verbose=True, **kwargs):
        'Confirm the changes.'
        prompt = '{0.YELLOW}Replace? [Y/n/q]: {0.RESET}'.format(colorama.Fore)
        while True:
            try:
                choice = input(prompt).lower()
            except EOFError:
                choice = 'q'

            if choice in {'yes', 'y', ''}:
                return self._save(*args, **kwargs, verbose=verbose)
            elif choice in {'no', 'n'}:
                self.ignored += 1
                return
            elif choice in {'quit', 'q'}:
                self.ignored += 1
                self._show_stat()
                sys.exit()
            else:
                self._invalid(choice)

    @staticmethod
    def _invalid(command):
        'Print warning message for invalid operations.'
        message = '{0.RED}Invalid operation: {0.RESET}{1}'
        print(message.format(colorama.Fore, command))

    @staticmethod
    def _retry(func, max_retries=5, interval=60, min_interval=10):
        'Retry operation in case of failure.'

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            for count in range(max_retries):
                try:
                    func(self, *args, **kwargs)
                except mwclient.ProtectedPageError:
                    self.errors += 1
                    return
                except mwclient.MwClientError as err:
                    print('{0.__class__.__name__}: {0}'.format(err))
                    if count == max_retries - 1:
                        self.errors += 1
                        return
                    else:  # incremental backoff strategy
                        time.sleep(max(count * interval, min_interval))
                else:
                    self.edited += 1
                    return

        return wrapper

    @_retry.__func__
    def _save(self, page, result, verbose=False):
        'Commit changes to MediaWiki.'
        if verbose is True:
            print('Saving...', end=' ')

        page.save(result, self.edit_summary, self.minor)

        if verbose is True:
            print('Done.')
        elif verbose:
            print(verbose, end='')

    def _show_stat(self):
        'Show the number of edited and ignored pages.'
        items = ['total', 'edited', 'ignored', 'errors']
        self.total = sum(getattr(self, i) for i in items[1:])
        pattern = ', '.join('{{0.{0}}} {0}'.format(i) for i in items)
        message = '\n{0.RED}{1}{0.RESET}'
        print(message.format(colorama.Fore, pattern.format(self)), sep='')


def read_config(filenames, section=configparser.DEFAULTSECT):
    'Read the configuration file.'
    config = configparser.ConfigParser(default_section=section)
    config.read(filenames)

    result = collections.OrderedDict()
    items = config[section]
    for key in items:
        # skip empty items
        if not items[key]:
            continue
        # try to convert other items
        for data_type in 'boolean', 'int', 'float', '':
            converter = getattr(items, 'get' + data_type)
            try:
                result[key] = converter(key)
            except ValueError:
                pass
            else:
                break
    return result


def main(bot, argc=2, argv=sys.argv):
    'Parse command line options.'
    try:
        assert argc <= len(argv) <= argc + 1
        b = bot(**read_config('bot.ini', 'general'))
        b(*argv[1:])
    except AssertionError:  # print the docstring as help message
        import __main__
        print(__main__.__doc__.format(argv[0]))
    except KeyboardInterrupt:
        if 'b' in vars():
            b._show_stat()
        else:
            print('Cancelled.')


if __name__ == '__main__':
    main(Bot)
