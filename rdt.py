#!/usr/bin/env python3

'''Convert route diagram templates from {{BS-table}} to {{Routemap}}.
'''

import re
import sys


def parse_rdt(line: str) -> str:
    line = line[:-2]  # remove trailing braces '}}'

    template, *params = line.split('|')
    template_type = re.match(r'(?a)^\{\{BS(\d*)$', template)
    if not template_type:
        return line
    n = int(template_type.group(1) or 1)

    icons, params = params[:n], params[n:]

    # remove empty cells
    while params and params[-1] == '':
        params.pop()
    while icons[0] == icons[-1] == '':
        icons.pop(0)
        icons.pop()

    params.insert(0, '\\'.join(icons))

    # prevent '~~~~'
    for i, param in enumerate(params):
        if not param:
            params[i] = ' '

    return '~~'.join(params)


if __name__ == '__main__':
    print('{{Routemap|map=')
    for line in sys.stdin:
        print(parse_rdt(line.strip()))
    print('}}')
