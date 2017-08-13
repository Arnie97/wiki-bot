#!/usr/bin/env python3

'''Add WikiProject banners to talk pages.

Usage: {0} <templates> <banner> <edit-summary> [minor]
Example: {0} "bd,BD" "WikiProject Biography" "Add banner" m
'''

import functools
import gevent
import gevent.lock
import gevent.monkey
import gevent.pool
gevent.monkey.patch_all()

from bot import Bot, main


class BannerBot(Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = gevent.lock.BoundedSemaphore()
        self.pool = gevent.pool.Pool(100)

    def __call__(self, templates, banner, edit_summary, minor=False):
        'Iterate through articles embedding the specified templates.'
        super().__call__(edit_summary, minor)

        # get all possible variants of the WikiProject banner
        ns = 'Template:'
        banner_page = self.site.pages[ns + banner]
        self.variants = self._variants(banner_page)

        # check all pages embedding the specified templates
        with open(__file__ + '.log', 'a', encoding='utf-8') as f:
            for tl in templates.split(','):
                pages = self.site.pages[ns + tl].embeddedin()
                for page in self.pool.imap(self._evaluate, pages):
                    print(page.pageid, page.name, sep='\t', file=f)

        self._show_stat()

    @staticmethod
    def _pipe(func):
        'Return the first parameter for pipelines.'

        @functools.wraps(func)
        def wrapper(self, param, *args, **kwargs):
            func(self, param, *args, **kwargs)
            return param

        return wrapper

    @_pipe.__func__
    def _evaluate(self, page):
        'Analyze the page contents to decide the next step.'
        if page.namespace:  # not articles
            return next(self)
        else:  # navigate to its talk page
            page = self.site.pages['Talk:' + page.name]

        # find template messages in the talk page
        contents = page.text()
        already_included = any('{{' + tl in contents for tl in self.variants)
        if already_included:
            return next(self)
        else:
            result = '{{%s}}\n%s' % (self.variants[-1], contents)

        if self.minor:  # automatic mode
            self._save(page, result, '*' if page.exists else '#')
        else:  # manual mode
            self._info(page)
            self._confirm(page, result)

    def _save(self, *args, **kwargs):
        self.lock.acquire()
        super()._save(*args, **kwargs)
        self.lock.release()


if __name__ == '__main__':
    main(BannerBot, argc=4)
