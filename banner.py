#!/usr/bin/env python3

'''Add WikiProject banners to talk pages.

Usage: {0} <templates> <banner> <edit-summary> [minor]
Example: {0} "bd,BD" "WikiProject Biography" "Add banner" m
'''

import sys
import colorama
import replace


class BannerBot(replace.ReplaceBot):
    'Add WikiProject banners to talk pages.'

    def __call__(self, templates, banner, edit_summary, minor_edit=False):
        'Iterate through articles embedding the specified templates.'
        self.edit_summary = edit_summary
        self.minor_edit = minor_edit
        self.edited = 0
        self.ignored = 0

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

    @staticmethod
    def __next__():
        'Simple progress indicator.'
        print('.', end='')

    def _evaluate(self, page):
        'Analyze the page contents to decide the next step.'
        if page.namespace:  # not articles
            self.ignored += 1
            return next(self)
        else:  # navigate to its talk page
            page = self.site.pages['Talk:' + page.name]

        # find template messages in the talk page
        contents = page.text()
        already_included = any('{{' + tl in contents for tl in self.variants)
        if already_included:
            self.ignored += 1
            return next(self)

        print(
            '\n',
            colorama.Fore.CYAN, page.name,
            colorama.Fore.GREEN, ' (', page.length, ')',
            colorama.Fore.RESET, sep=''
        )
        self._choose_action(page, contents)

    def _replace(self, page, contents):
        'Commit changes to Wikipedia.'
        print('Saving...', end=' ')
        contents = '{{%s}}\n%s' % (self.variants[-1], contents)
        page.save(contents, self.edit_summary, self.minor_edit)
        print('Done.')


def main(argv):
    try:
        assert 4 <= len(argv) <= 5
        bot = BannerBot()
        bot(*argv[1:])
    except AssertionError:
        print(__doc__.format(argv[0]))


if __name__ == '__main__':
    main(sys.argv)
