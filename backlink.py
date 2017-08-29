#!/usr/bin/env python3

'''Fix backlinks after moving a page.

Usage: {0} <page> <src> <dest> <edit-summary> [minor]
Example: {0} P A B "Fix links: A was moved to B" m

The example above will modify links in page P following these rules:

* [A] -> [B|A]
* [A|B] -> [B]
* [A|C] -> [B|C]
'''

import re
from bot import Bot, main


class BacklinkBot(Bot):

    def __call__(self, title, src, dest, edit_summary, minor=False):
        'Iterate through backlinks.'
        super().__call__(edit_summary, minor)
        self._evaluate(self.site.pages[title], src, dest)

    def _evaluate(self, page, src, dest):
        'Generate regular expression rules.'
        rsrc, rdest = re.escape(src), re.escape(dest)
        self._contents = page.text()
        self._locals = locals()
        self._replace(r'({rsrc})', r'{dest}|\1')
        self._replace(r'{rsrc}\|({rdest})', r'\1')
        self._replace(r'{rsrc}\|([^\]|]+)', r'{dest}|\1')
        self._confirm(page, self._contents)

    def _replace(self, pattern, replace):
        'Do regular expression substitute.'
        pattern = r'\[\[%s\]\]' % pattern.format(**self._locals)
        replace = r'[[%s]]'     % replace.format(**self._locals)
        self._contents = re.sub(pattern, replace, self._contents)


if __name__ == '__main__':
    main(BacklinkBot, argc=5)
