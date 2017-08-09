#!/usr/bin/env python3

'''Add WikiProject banners to talk pages.

Usage: {0} <templates> <banner> <edit-summary> [minor]
Example: {0} "bd,BD" "WikiProject Biography" "Add banner" m
'''

from bot import Bot, main


class BannerBot(Bot):

    def __call__(self, templates, banner, edit_summary, minor=False):
        'Iterate through articles embedding the specified templates.'
        super().__call__(edit_summary, minor)

        # get all possible variants of the WikiProject banner
        ns = 'Template:'
        banner_page = self.site.pages[ns + banner]
        redirects = banner_page.backlinks(filterredir='redirects')
        self.variants = [p.page_title for p in redirects]
        self.variants.append(banner_page.page_title)

        # check all pages embedding the specified templates
        for tl in templates.split(','):
            for page in self.site.pages[ns + tl].embeddedin():
                self._evaluate(page)

        self._show_stat()

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
            self._save(page, result, verbose='#')
        else:  # manual mode
            self._info(page)
            self._confirm(page, result)


if __name__ == '__main__':
    main(BannerBot, argc=4)
