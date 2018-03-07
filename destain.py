#!/usr/bin/env python3

'''Remove colored text from metro station articles.

Usage: {0} <cities> [minor]
Example: {0} nanchang,shenzhen m
'''

from bot import main
from regex import RegexBot


class DestainBot(RegexBot):
    '[[WP:鐵道專題/移除著色文字模板]]'

    def __call__(self, cities, minor=False):
        for city in cities.split(','):
            super().__call__(*globals()[city](), self.__doc__, minor)


def nanchang():
    template = '南昌地铁线路名'
    single_line = r'(\{\{%s\|\d+)\|block(\}\})' % template
    pattern = r'(?<=是\[\[南昌地铁\]\]){0}(?:(、){0})?(?=的)'
    pattern = (pattern + r'|{0}(?=站厅在|岛式|侧式)').format(single_line)
    repl = r'\1\2\3\4\5\6\7'
    return template, pattern, repl


def tianjin():
    template = '天津地铁线路名'
    pattern = r'\{\{%s\|M?(Z?\d+)\|\w+\}\}' % template
    repl = r'{{天津轨道交通线路名|\1|c}}'
    return template, pattern, repl


if __name__ == '__main__':
    main(DestainBot)
