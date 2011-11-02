#!/usr/bin/env python
# encoding: utf-8

'''
This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
COPYING for more details.
'''

import argparse
import re as regex

parser = argparse.ArgumentParser(description='Converts pgAdmin3 data dumps to DDL scripts')
parser.add_argument('infile', type=file, help='The pgAdmin3 data dump file to convert')
parser.add_argument('outfile', type=argparse.FileType('w'), help='The output file to write to')
parser.add_argument('-I', '--sortidx', metavar='n', type=int, default=0, help='The column to use when sorting data. Default is 0.')
parser.add_argument('-T', '--tables', metavar='table', nargs='+', type=str, help='Tables to export')
args = parser.parse_args()

fin = args.infile
fout = args.outfile

content = fin.read()
lines = content.split('\n')

def parse_definition(str):
    # 'COPY {definition} FROM stdin;'
    return str[5:-12]

def export_table(table, out):
    global args
    
    definition = table[0]
    table_name = definition.split()[0]
    if args.tables != None and table_name not in args.tables:
        return
        
    print("Exporting table %s" % table_name)
    out.write('-- %s\n' % definition)
    del table[0]
    
    if args.sortidx != None:
        try:
            table = sorted(table, key=lambda x: int(x.split('\t')[args.sortidx]))
        except ValueError: pass # Column is not a number
    
    for line in table:
        line = "'" + line.replace('\\N', 'null');
        line = "', '".join(line.replace('\n', '').split('\t'))
        line = regex.sub(r"'?null'?", 'null', line)
        if not line.endswith('null'):
            line += "'"
        line = line.replace("'f'", "'0'").replace("'t'", "'1'")
        
        out.write("INSERT INTO {1} VALUES ({0});\n".format(line, definition));
    
    out.write('\n\n')


count = content.count('\nCOPY')
print('Found %d table%s' % (count, "s" if count > 1 else ""))

in_table = False
table = []
for line in lines:
    if not in_table and line.startswith('COPY'):
        in_table = True
        table.append(parse_definition(line))
        continue
    
    if in_table and line.startswith('\\.'):
        export_table(table, fout)
        in_table = False
        table = []
    
    if in_table:
        table.append(line)
    
fin.close()
fout.close()

