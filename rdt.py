#!/usr/bin/env python3

'''Convert route diagram templates from {{BS-table}} to {{Routemap}}.
'''

import re
import sys
from bot import Bot


class RDTConverter(Bot):

    def __init__(self):
        'Use English Wikipedia to substitute the templates.'
        super().__init__('en.wikipedia.org')

    def __call__(self, wikitext: str) -> str:
        'Perform the conversions.'
        wikitext = self._add_safesubst(wikitext)
        result = self._parse_pst(wikitext).strip()

        if not result.startswith('{{'):
            result = '{{Routemap|map=\n' + result
        if not result.endswith('}}'):
            result += '\n}}'
        return result

    @staticmethod
    def _add_safesubst(wikitext: str) -> str:
        'Add safesubst modifiers to the templates.'
        pattern = r'''(?ax)
            (\{\{)
                (BS-?\w*|Railway\ line\ header)
                /?\w*  # {{BS-table/WithCollapsibles}}
            (\}\}|\|)
        '''
        repl = r'\1{0}:\2/{0}\3'.format('safesubst')
        return re.sub(pattern, repl, wikitext)

    def _parse_pst(self, wikitext: str) -> str:
        'Do a pre-save transform on the input.'
        api = 'parse'
        return self.site.post(
            api, text=wikitext, contentmodel='wikitext',
            onlypst=True
        )[api]['text']['*']


if __name__ == '__main__':
    bot = RDTConverter()
    print('\n', bot(sys.stdin.read()))
