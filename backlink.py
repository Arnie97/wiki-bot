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

    rules = [
        (r'({rsrc})', r'{dest}|\1'),
        (r'(?:{rsrc})\|({rdest})', r'\1'),
        (r'(?:{rsrc})\|([^\]|]+)', r'{dest}|\1'),
    ]

    def __call__(self, title, src, dest, edit_summary, minor=False):
        'Iterate through backlinks.'
        super().__call__(edit_summary, minor)
        rsrc = '|'.join(map(re.escape, self._dialects(src)))
        self._replace(self.site.pages[title], rsrc, dest, raw=True)

    def _replace(self, page, src, dest, raw=False):
        'Do regular expression substitute.'
        rsrc = src if raw else re.escape(src)
        rdest = re.escape(dest)
        contents = page.text()
        for pattern, replace in self.rules:
            pattern = r'\[\[%s\]\]' % pattern.format(**locals())
            replace = r'[[%s]]'     % replace.format(**locals())
            contents = re.sub(pattern, replace, contents)
        self._save(page, contents, verbose=True)


if __name__ == '__main__':
    main(BacklinkBot, argc=5)
