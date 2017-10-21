#!/usr/bin/env python3

r'''Regular expression substitution bot.

Usage: {0} <pattern> <repl> <edit-summary> [minor]
Example: {0} "\(([A-Z a-z-]+)）" "（\1）" "Fix parentheses"
Example: {0} "（([A-Z a-z-]+)\)" "（\1）" "Fix parentheses"
'''

import re
from bot import Bot, main
from replace import ReplaceBot
from regex import RegexBot


class RegexReplaceBot(RegexBot, ReplaceBot):

    def __call__(self, pattern, repl, edit_summary, minor=False):
        'Search the MediaWiki site with regular expression.'
        Bot.__call__(self, edit_summary, minor)
        self.pattern = pattern
        self.repl = repl

        for item in self.site.search('insource:/%s/' % pattern):
            page = self._parse(item)
            self._evaluate(page)

        self._show_stat()

    def _replace(self, page, contents):
        'Do regular expression substitute and preview the changes.'
        result = re.sub(self.pattern, self.repl, contents)
        self._save(page, result)


if __name__ == '__main__':
    main(RegexReplaceBot, argc=4)
