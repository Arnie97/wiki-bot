#!/usr/bin/env python3

'''Regular expression substitution bot.

Usage: {0} <templates> <pattern> <repl> <edit-summary> [minor]
'''

import re
import colorama
from bot import Bot, main


class RegexBot(Bot):

    def __call__(self, template, pattern, repl, edit_summary, minor=False):
        'Iterate through pages transcluding from the template.'
        super().__call__(edit_summary, minor)
        self.pattern = pattern
        self.repl = repl
        self.keywords = ['{{' + template]  # for diff preview

        ns = 'Template:'
        for page in self.site.pages[ns + template].embeddedin():
            self._evaluate(page)

        self._show_stat()

    def _evaluate(self, page):
        'Analyze the page contents to decide the next step.'
        if page.namespace in [0, 10]:  # only articles and templates
            contents = page.text()
            if re.search(self.pattern, contents):
                return self._replace(page, contents)

        return next(self)

    def _replace(self, page, contents):
        'Do regular expression substitute and preview the changes.'
        self._info(page)
        self._preview(contents, '-', colorama.Fore.RED)
        result = re.sub(self.pattern, self.repl, contents)
        self._preview(result, '+', colorama.Fore.GREEN)
        self._confirm(page, result)


if __name__ == '__main__':
    main(RegexBot, argc=5)
