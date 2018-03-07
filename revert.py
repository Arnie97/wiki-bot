#!/usr/bin/env python3

'''Revert wrong edits made by this robot.

Usage: {0} <page> <edit-summary> [minor]
Example: {0} CRH "Revert wrong edit" m
'''

import sys
from bot import Bot, main


class RevertBot(Bot):

    def __call__(self, title, edit_summary, minor=False):
        'Fetch the pages.'
        super().__call__(edit_summary, minor)
        while True:
            try:
                self._replace(self.site.pages[input('> ')])
            except EOFError:
                self._show_stat()
                sys.exit()
            except Exception as err:
                print('{0.__class__.__name__}: {0}'.format(err))

    def _replace(self, page):
        'Check the edit history and revert to the previous version.'
        revisions = page.revisions(limit=2, prop='ids|user|content')
        last_revision = next(revisions)
        if last_revision['user'] != self.site.username:
            msg = 'Skip page "{0}" (last revision {1[revid]} by {1[user]}).'
            print(msg.format(page.name, last_revision))
            self.ignored += 1
        else:
            prev_revision = next(revisions)
            self._save(page, prev_revision['*'])


if __name__ == '__main__':
    main(RevertBot)
