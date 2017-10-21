#!/usr/bin/env python3

'''Add WikiProject banners for T:Infobox rail-system route.

Usage: {0} <edit-summary> [minor]
Example: {0} "Add banner" m
'''

from banner import BannerBot, main


class RailBannerBot(BannerBot):

    projects = {
        '鐵道專題': '客運專線,高速鐵路',
        '城市軌道交通專題': '捷運,地鐵,輕軌,電車,軌道交通',
        '巴士專題': '巴士,公交,BRT'
    }

    def __init__(self, *args, **kwargs):
        'List variants of the page and the keywords.'
        super().__init__(*args, **kwargs)
        self.variants = []
        self.keywords = {}
        ns = 'Template:'
        for p, keys in self.projects.items():
            self.variants.extend(self._variants(self.site.pages[ns + p]))
            self.keywords[p] = set()
            print('Parsing keyword variants...', end=' ')
            for k in keys.split(','):
                print(k, end=' ')
                self.keywords[p].update(self._dialects(k))
            print('Done.')

    def __call__(self, edit_summary, minor=False):
        'Check all pages embedding the specified template.'
        super(BannerBot, self).__call__(edit_summary, minor)
        tl = 'T:Infobox rail system-route'
        with open(__file__ + '.log', 'a', encoding='utf-8') as f:
            pages = self.site.pages[tl].embeddedin()
            for title in self.pool.imap(self._evaluate, pages):
                if title:
                    print(title, file=f)
        self._show_stat()

    def _evaluate(self, page):
        'Analyze the talk page to decide the next step.'
        if page.namespace or page.redirect:  # not articles
            return next(self)
        else:  # navigate to its talk page
            page = self.site.pages['Talk:' + page.name]
            if page.redirect:  # redirect page
                return next(self)

        # find template messages in the talk page
        contents = page.text()
        already_included = any('{{' + tl in contents for tl in self.variants)
        if already_included:
            return next(self)

        for p, keywords in self.keywords.items():
            if any(k in page.name for k in keywords):
                banner = p
                sure = True
                break
        else:
            banner = '鐵道專題'
            sure = False

        result = '{{%s}}\n%s' % (banner, contents)
        self._save(page, result, '*' if page.exists else '#')

        if not sure:
            return page.page_title


if __name__ == '__main__':
    main(RailBannerBot)
