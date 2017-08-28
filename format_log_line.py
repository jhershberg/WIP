#!/usr/bin/python

import string
from sys import stdout,stdin,argv,exit

line_num = 0
def nl():
    global line_num
    line_num += 1
    stdout.write('\n' + i)

for l in stdin:
    msg = l

    I = '  '
    opener = '[{<'
    closer = ']}>'
    i = ''

    in_ws = 1
    is_empty_list = 0
    last_char = ''
    title = ''
    title_stack = []
    in_string_constant = 0

    for c in msg:
        if in_ws and c in ' \t': continue
        in_ws = 0

        if c in closer:
            i = i[:-2]
            if not is_empty_list and last_char not in closer: nl()
            in_ws = 1
            is_empty_list = 0
            title = ''
        elif is_empty_list:
            is_empty_list = 0
            nl()

        if last_char in closer and c != ',': nl()

        stdout.write(c)
        #if not c in opener: title += c
        last_char = c


        if in_string_constant:
            pass

        if c == '"':
            if in_string_constant: in_string_constant = 0
            else: in_string_constant = 1
            
        elif c in closer:
            if len(title_stack):
                (t,ln) = title_stack.pop()
                if (line_num - ln) > 5: stdout.write(' /* ' + t.strip() + ' */')

        elif c in opener:
            i += I
            in_ws = 1
            is_empty_list = 1
            if title:
                title_stack.append((title, line_num))
                title = ''

        elif c == ',' and not in_string_constant:
            nl()
            in_ws = 1
            title = ''
