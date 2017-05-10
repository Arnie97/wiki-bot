#!/usr/bin/env python3

import re
import colorama
import replace


class RailwayBot(replace.ReplaceBot):

    def __init__(self, site, **kwargs):
        'Load the telegraph code database.'
        super().__init__(site, **kwargs)

        self.template = 'Template:Infobox China railway station'
        self.keywords = ['电报码', '拼音码']
        self.name_pattern = '(\w+)站'

        # https://kyfw.12306.cn/otn/resources/js/framework/station_name.js
        with open('station_name.js', encoding='utf-8') as fp:
            # skip javascript stuff around single quotes
            # skip the first '@' character in the string
            packed_stations = fp.read().split("'")[1][1:]

        self.stations = {}
        for s in packed_stations.split('@'):
            lst = s.split('|')
            self.stations[lst[1]] = [lst[0].upper(), lst[2]]

    def __call__(self, edit_summary, minor_edit=True):
        'Iterate through instances of the railway station template.'
        self.edit_summary = edit_summary
        self.minor_edit = minor_edit

        self.unknown = 0
        self.ignored = 0
        self.edited = 0

        for page in self.site.pages[self.template].embeddedin():
            self._evaluate(page)

        self._show_stat()

    def _convert(self, **kwargs):
        'Convert between language variants, such as zh-CN and zh-TW.'
        return self.site.get('parse', **kwargs)['parse']['displaytitle']

    def _normalize(self, pageid):
        'Get normalized station name from page id.'
        simplified = self._convert(pageid=pageid, uselang='zh-CN')
        match = re.match(self.name_pattern, simplified)
        return match.group(1) if match else ''

    def _evaluate(self, page):
        normalized = self._normalize(page.pageid)

        # exclude pages with telecode
        content = page.text()
        included = all(keyword in content for keyword in self.keywords)

        choose_action = False
        if included:
            prompt = 'OK'
            self.ignored += 1
        elif not normalized or normalized not in self.stations:
            prompt = colorama.Fore.MAGENTA + normalized + '?'
            self.unknown += 1
        else:
            prompt = colorama.Fore.YELLOW + self.stations[normalized][1]
            choose_action = True
        print(
            colorama.Fore.CYAN,
            page.name,
            colorama.Fore.GREEN,
            ' (', str(page.length), ')',
            colorama.Fore.RESET,
            ' -> ', prompt,
            colorama.Fore.RESET,
            sep=''
        )
        if choose_action:
            self._choose_action(page.name)


if __name__ == '__main__':
    bot = RailwayBot('zh.wikipedia.org', clients_useragent='Arnie97-Bot')
    bot('信息框：添加电报码', minor_edit=False)
