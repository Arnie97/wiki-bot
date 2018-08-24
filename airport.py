#!/usr/bin/env python3

'''Create redirects from airport codes.

Usage: {0} <edit-summary> [minor]
Example: {0} "Create new redirect" m
'''

import re
import gevent.monkey
import gevent.pool
from bot import Bot, main


class AirportBot(Bot):

    template = 'Template:Infobox Airport'
    patterns = [
        r'\b%s\s*=\s*([A-Z]{%d})\b' % pair
        for pair in dict(IATA=3, ICAO=4).items()
    ]
    repl = '#REDIRECT [[{page.name}]]'

    def __call__(self, edit_summary, minor=False):
        'Check all pages onto which the airport infobox is transcluded.'
        super().__call__(edit_summary, minor)
        pages = self.site.pages[self.template].embeddedin()
        for page in gevent.pool.Pool(100).imap(self._parse, pages):
            pass
        self._show_stat()

    def _parse(self, page):
        'Extract the airport codes from articles.'
        if page.namespace:  # not in the article namespace, hence ignore it
            return next(self)
        for pattern in self.patterns:
            match = re.search(pattern, page.text())
            if match:
                self._create_redirect(page, airport_code=match.group(1))

    def _create_redirect(self, page, airport_code):
        'Create a redirect page if the page title does not exist yet.'
        redirect_page = self.site.pages[airport_code]
        if redirect_page.exists:
            return next(self)
        else:
            self._save(redirect_page, self.repl.format_map(vars()), '#')


if __name__ == '__main__':
    gevent.monkey.patch_all()
    main(AirportBot)
