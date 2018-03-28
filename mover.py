#!/usr/bin/env python3

'''Move a parenthetical disambiguation page to the correct title.

Usage: {0} <corrected> <edit-summary> [minor]
'''

import re
import colorama
from bot import main
from regex import RegexBot


class PageMover(RegexBot):

    disambig_pattern = r'(\S+) \((\S+)\S\)'

    def __call__(self, title, edit_summary, minor=False):
        'The main routine.'
        super(RegexBot, self).__call__(edit_summary, minor)
        target = self.site.pages[title]
        source = self._inspect(target)
        if source:
            self._move_links(source, target)
            self._request_delete(source)

    def _inspect(self, target):
        'Inspect the current title of the article.'
        match = re.fullmatch(self.disambig_pattern, target.name)
        if not match:
            print('The title of the target is not parenthetical.')
            return next(self)
        for title in self._remove_trailing(target.name):
            page = self.site.pages[title]
            if page.exists:
                message = '{0.CYAN}{1.name} -> {2.name}{0.RESET}'
                print(message.format(colorama.Fore, page, target))
                break
        else:
            print('Failed to inspect the incorrect previous title.')
            return next(self)

        if target.exists and not target.redirect:
            if page.redirect and page.redirects_to().pageid == target.pageid:
                print('The page is already moved to the target name.')
                return page
            elif page.redirect:
                print('The source page redirects to somewhere else now!')
                return next(self)
            else:
                print('Neither page is a redirect page!')
                return next(self)
        elif target.redirect and target.redirects_to().pageid != page.pageid:
            print('The target page redirects to somewhere else now!')
            return next(self)
        elif self._confirm(page, target.name, move=True):
            return page

    def _remove_trailing(self, old):
        'Remove the last character in the parentheses.'
        while True:
            new = re.sub(self.disambig_pattern, r'\1 (\2)', old)
            if old != new:
                old = new
                yield new
            else:
                return

    def _move_links(self, src, dest):
        'Modify all the backlinks.'
        dialects = self._dialects(src.name)
        dialects = sum(([d.replace(' ', '_'), d] for d in dialects), [])
        self.pattern = r'\b(%s)' % '|'.join(map(re.escape, dialects))
        self.repl = dest.name
        self.keywords = dialects + [dest.name]

        for page in src.backlinks(redirect=False):
            self._replace(page, page.text())

        remaining = ' '.join(p.name for p in src.backlinks())
        if remaining:
            print('Backlinks left behind:', remaining)
        else:
            print('Backlinks clear.')

    def _request_delete(self, page):
        'Request speedy deletion.'
        message = '{0.CYAN}{1.name} -> {0.RED}DELETE{0.RESET}'
        print(message.format(colorama.Fore, page))
        self._confirm(page, '{{d|R3|G10}}')

    def _save(self, page, result, verbose=False, move=False):
        'Request a page move.'
        if not move:
            return super()._save(page, result, verbose)

        if verbose is True:
            print('Moving...', end=' ')

        page.move(result, self.edit_summary)

        if verbose is True:
            print('Done.')
        elif verbose:
            print(verbose, end='')
        return True


if __name__ == '__main__':
    main(PageMover, argc=3)
