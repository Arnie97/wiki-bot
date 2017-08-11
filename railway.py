#!/usr/bin/env python3

'''Add telegraph code to China railway station articles.

Usage: {0} <edit-summary> [minor]
Example: {0} "Add telegraph code" m
'''

import re
import colorama
from bot import Bot, main


class RailwayBot(Bot):

    template = 'Template:Infobox China railway station'
    keywords = ['电报码', '拼音码']
    repl = '|电报码 = {1}\n|拼音码 = {0}\n'
    fields = '(车站|其他|英文)(名称(拼音)?|拼音|代码)'

    name_pattern = r'(\w+)站'
    param_pattern = r'\|\s*(%s)\s*=\s*{}(?=\|)'
    valid_pattern = param_pattern.format(r'[A-Z]{3}[\s\S]*')
    field_pattern = param_pattern.format(r'[^<{[\]}>|]*')

    def __init__(self, *args, **kwargs):
        'Load the telegraph code database.'
        super().__init__(*args, **kwargs)

        # https://kyfw.12306.cn/otn/resources/js/framework/station_name.js
        with open('station_name.js', encoding='utf-8') as fp:
            # skip javascript stuff around single quotes
            # skip the first '@' character in the string
            packed_stations = fp.read().split("'")[1][1:]

        self.stations = {}
        for s in packed_stations.split('@'):
            lst = s.split('|')
            self.stations[lst[1]] = [lst[0].upper(), lst[2]]

    def __call__(self, edit_summary, minor=False):
        'Iterate through instances of the railway station template.'
        super().__call__(edit_summary, minor)
        self.unknown = 0

        for page in self.site.pages[self.template].embeddedin():
            self._evaluate(page)

        self._show_stat()

    def _normalize(self, pageid):
        'Get normalized station name from page id.'
        simplified = self._convert(pageid=pageid, uselang='zh-CN')
        match = re.match(self.name_pattern, simplified)
        return match.group(1) if match else ''

    def _evaluate(self, page):
        'Analyze the page contents to decide the next step.'
        normalized = self._normalize(page.pageid)

        # exclude pages with telecode, but not pages with empty parameters
        contents = page.text()
        included = any(
            keyword in contents
            for keyword in self.keywords)
        complete = all(
            re.search(self.valid_pattern % keyword, contents)
            for keyword in self.keywords)

        # does not perform any action by default
        action = False

        if complete:
            prompt = 'OK'
            self.ignored += 1
        elif not normalized:
            prompt = colorama.Fore.RED + 'X'
            self.errors += 1
        elif normalized not in self.stations:
            prompt = colorama.Fore.MAGENTA + normalized + '?'
            self.unknown += 1
        else:
            prompt = colorama.Fore.YELLOW + self.stations[normalized][1]
            action = True

        self._info(page, ' -> ', prompt, end='')

        if action:
            self._replace(page, self.stations[normalized], included)

    def _replace(self, page, data, existing=False):
        'Do regular expression substitute and preview the changes.'
        print()  # line break
        s = page.text()
        self._preview(s, '-', colorama.Fore.RED)

        # remove existing parameters
        if existing:
            fields = '|'.join(self.keywords)
            s = re.sub(self.field_pattern % fields, '', s)

        # get the last occurrence
        for match in re.finditer(self.field_pattern % self.fields, s):
            pass

        # insert telegraph code after the match
        i = match.end()
        result = ''.join((s[:i], self.repl.format(*data), s[i:]))
        self._preview(result, '+', colorama.Fore.GREEN)

        self._confirm(page, result)


if __name__ == '__main__':
    main(RailwayBot)
