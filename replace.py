#!/usr/bin/env python3

'''Simple find-and-replace bot.

Usage: {0} <pattern> <repl> <edit-summary> [minor]
Example: {0} infomation information "Fix typo" m
'''

import html
import colorama
from bot import Bot, main


class ReplaceBot(Bot):

    def __call__(self, pattern, repl, edit_summary, minor=False):
        'Search the MediaWiki site.'
        super().__call__(edit_summary, minor)
        self.keywords = [pattern, repl]

        for item in self.site.search('"%s"' % pattern):
            self._evaluate(item)

        self._show_stat()

    def _evaluate(self, item):
        'Highlight keywords in the article.'
        page = self.site.pages[item['title']]
        self._info(page)
        print(html.unescape(
            item['snippet']
            .replace('<span class="searchmatch">', colorama.Fore.MAGENTA)
            .replace('</span>', colorama.Fore.RESET)
        ))
        self._replace(page)

    def _replace(self, page):
        'Performs the replacement and preview the changes.'
        original_text = page.text()
        replaced_text = original_text.replace(*self.keywords)
        if not self.minor:
            self._preview(original_text, '-', colorama.Fore.RED)
            self._preview(replaced_text, '+', colorama.Fore.GREEN)
        self._confirm(page, replaced_text)


if __name__ == '__main__':
    main(ReplaceBot, argc=4)
