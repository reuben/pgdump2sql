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

parser = argparse.ArgumentParser(description='Converts pgAdmin3 data dumps to DDL scripts')
parser.add_argument('infile', type=file, help='The pgAdmin3 data dump file to convert')
parser.add_argument('outfile', type=argparse.FileType('w'), help='The output file to write to')
parser.add_argument('-I', '--sortidx', metavar='n', type=int, default=0, help='The column to use when sorting data. Default is 0.')
args = parser.parse_args()

fin = args.infile
fout = args.outfile

def parse_definition(str):
    # 'COPY {definition} FROM stdin;'
    return str[5:-13]

definition = ""

# Copy the actual data to our lines array
lines = []
append = False
for l in fin:
    if not append and l.startswith('COPY'):
        definition = parse_definition(l)
        append = True
        continue
    if append and l.startswith('\\.'):
        break
    if append:
        lines.append(l)
    

if args.sortidx != None:
    lines = sorted(lines, key=lambda x: int(x.split('\t')[args.sortidx]))

for l in lines:
    l = l.replace('\\N', 'null');
    fout.write("INSERT INTO {1} VALUES ('{0}');\n"
                    .format("', '".join(l.split('\t')).replace('\n', '').replace("'null'", 'null'), definition));

fin.close()
fout.close()
