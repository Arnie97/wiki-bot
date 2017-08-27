#!/usr/bin/env python3

from replace import ReplaceBot


class PunctuationBot(ReplaceBot):

    def _replace(self, page):
        blacklist = self.blacklist.split('|')
        original_text = page.text()

        if page.namespace:  # not articles
            return next(self)
        elif any(rule in original_text for rule in blacklist):
            return next(self)
        else:
            replaced_text = original_text.replace(*self.keywords)
            self._confirm(page, replaced_text)


if __name__ == '__main__':
    bot = PunctuationBot('zh.wikipedia.org')
    bot.blacklist = '漢字|汉字|部首|筆畫|標點|假名|Unicode|四角|輸入法'
    bot('丶', '、', '修正标点', minor=True)
