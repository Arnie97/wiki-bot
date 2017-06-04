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
        self.keyword_pattern = r'\|\s*%s\s*=\s*[A-Z]{3}\W'
        self.name_pattern = '(\w+)站'
        self.field_pattern = r'(\|\s*(%s)\s*=[^<{[\]}>|]*)(?=\|)' % \
            '(车站|其他|英文)(名称(拼音)?|拼音|代码)'
        self.repl_pattern = '|电报码 = {1}\n|拼音码 = {0}\n'

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

        self.ignored = 0
        self.error = 0
        self.unknown = 0
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
        'Analyze the page contents to decide the next step.'
        normalized = self._normalize(page.pageid)

        # exclude pages with telecode, but not pages with empty parameters
        contents = page.text()
        included = any(
            keyword in contents
            for keyword in self.keywords)
        complete = all(
            re.search(self.keyword_pattern % keyword, contents)
            for keyword in self.keywords)

        # does not perform any action by default
        action = False

        if complete:
            prompt = 'OK'
            self.ignored += 1
        elif not normalized:
            prompt = colorama.Fore.RED + 'X'
            self.error += 1
        elif normalized not in self.stations:
            prompt = colorama.Fore.MAGENTA + normalized + '?'
            self.unknown += 1
        else:
            prompt = colorama.Fore.YELLOW + self.stations[normalized][1]
            action = True

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

        if not action:
            return
        elif included:
            self._choose_action(page, self.stations[normalized])
        else:
            self._replace(page, self.stations[normalized])
            self.edited += 1

    def _replace(self, page, data):
        print('Saving...', end=' ')
        s = page.text()

        # get the last occurrence
        for match in re.finditer(self.field_pattern, s):
            pass

        # insert telegraph code after the match
        i = match.end()
        result = ''.join((s[:i], self.repl_pattern.format(*data), s[i:]))

        page.save(result, self.edit_summary, self.minor_edit)
        print('Done.')


if __name__ == '__main__':
    bot = RailwayBot('zh.wikipedia.org', clients_useragent='Arnie97-Bot')
    bot('信息框：添加电报码', minor_edit=False)
