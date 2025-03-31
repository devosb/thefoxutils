#!/usr/bin/python3

import importlib.util
from fontTools.ttLib import TTFont
from palaso.unicode.ucd import UCD
import cssutils
from collections import OrderedDict
import re
import sys
import os
import argparse


def main():
    parser = argparse.ArgumentParser(description='Check character inventory of a TTF font')
    parser.add_argument('-b', '--block', help='Group ranges by block', action='store_true')
    parser.add_argument('-c', '--css', help='Output in CSS Unicode range format', action='store_true')
    parser.add_argument('-r', '--reverse', help='Reverse the comparison', action='store_true')
    parser.add_argument('subset', help='Character set to check')
    parser.add_argument('item', help='TTF font files to process', nargs='*')
    parser.add_argument('--version', action='version', version='%(prog)s ' + '0.1')
    args = parser.parse_args()

    ucd = UCD()
    block_names = get_block_names()

    subset_set = get_codepoints(args.subset)
    items = args.item
    if len(items) == 0:
        # only the subset has been specified, so compare the
        # subset to an empty set to see everything in the subset
        items = ['']

    multiple = True
    if len(items) == 1:
        multiple = False
    for item in items:
        if multiple:
            print(f'{item}:')
        item_set = get_codepoints(item)
        if args.reverse:
            differences_set = subset_set & item_set
        else:
            differences_set = subset_set - item_set
        differences = sorted(differences_set)
        if args.css:
            output_css(differences, ucd, block_names)
        elif args.block:
            output_block(differences, ucd, block_names)
        else:
            output_list(differences, ucd)


def get_block_names():
    names = dict()

    home = os.environ['HOME']
    value_aliases = 'pub/doc/Unicode/ucd/tus/PropertyValueAliases.txt'
    value_aliases_filename = os.path.join(home, value_aliases)
    with open(value_aliases_filename) as value_aliases_file:
        for line in value_aliases_file:
            if line.startswith('blk;'):
                alias = line.split(';')
                code = alias[1].strip()
                name = alias[2].strip()
                names[code] = name

    return names


def get_codepoints(item):
    if item.endswith('.nam'):
        if os.path.exists(item):
            codepoints = get_namelist(item)
        else:
            print(f'name file {item} does not exist')
            sys.exit(1)
    elif item.endswith('.ttf') or item.endswith('.otf') or item.endswith('.woff2'):
        codepoints = get_cmap(item)
    elif item.endswith('.css'):
        codepoints = get_range(item)
    elif item == '':
        codepoints = set()
    else:
        codepoints = get_charset(item)

    return codepoints


def get_charset(charset_name):
    # file containing the charset
    home = os.environ['HOME']
    charsets = 'builds/pyfontaine/fontaine/charsets/internals'
    charset_filename = os.path.join(home, charsets, charset_name + '.py')

    # load the charset file
    spec = importlib.util.spec_from_file_location('acharset', charset_filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules['acharset'] = module
    spec.loader.exec_module(module)
    import acharset

    # return the list of characters in the charset
    return set(acharset.Charset.glyphs)


def get_namelist(namefile_filename):
    # file containing the name list
    codepoints = set()
    with open(namefile_filename) as namefile:
        for line in namefile:
            usv = line.split()[0]
            codepoint = int(usv, 16)
            codepoints.add(codepoint)

    # return the list of characters in the name file
    return codepoints


def get_range(css_filename):
    # CSS file
    codepoints = set()
    find_unicode_range = re.compile(r'u\+([0-9A-Fa-f]+)-?([0-9A-Fa-f]+)?')
    sheet = cssutils.parseFile(css_filename)
    for rule in sheet:
        if rule.type != rule.FONT_FACE_RULE:
            continue
        lines = rule._getCssText()
        for line in lines.splitlines():
            line_content = line.strip()
            if line_content.startswith('unicode-range:'):
                for unicode_range in line_content.split():
                    m = find_unicode_range.match(unicode_range)
                    if not m:
                        continue
                    start = int(m.group(1), 16)
                    if m.lastindex > 1:
                        # range of codepoints
                        end = int(m.group(2), 16)
                        codepoints.update(set(range(start, end+1)))
                    else:
                        # single codepoint
                        codepoints.add(start)

    return codepoints


def get_cmap(font_filename):
    # load cmap from the font
    font = TTFont(font_filename)
    cmap = font.getBestCmap()
    codepoints = set(cmap.keys())
    return codepoints


def output_list(differences, ucd):
    for char in differences:
        try:
            name = ucd.get(char, 'na')
        except KeyError:
            name = '(Unknown)'
        print(f'U+{char:04X} {name}')


def output_css(differences, ucd, block_names):
    output_ranges(differences, ucd, None, 'unicode-range: ', '-', ';')


def output_block(differences, ucd, block_names):
    output_ranges(differences, ucd, block_names, '|', '..U+', '')


def output_ranges(differences, ucd, block_names, prefix, sep, suffix):
    # Code (except for code involving blocks)
    # gratefully copied from https://github.com/LucasFonts/css-unicode-range
    blocks = OrderedDict()
    b = ''
    r = []
    for c in differences:
        if block_names:
            try:
                block = ucd.get(c, 'blk')
            except KeyError:
                block = '(Unknown)'
        else:
            block = 'SquashBlock'

        if block != b:
            if r:
                ranges.append(r)
            if b:
                blocks[b] = ranges
            ranges = []
            r = []
            b = block

        if r:
            if c - 1 == r[-1]:
                r.append(c)
            else:
                ranges.append(r)
                r = [c]
        else:
            r = [c]
    if r:
        ranges.append(r)
        blocks[block] = ranges

    for block_code, block_range in blocks.items():
        ur = []
        for r in block_range:
            if len(r) == 1:
                ur.append(f'U+{r[0]:04X}')
            else:
                u0 = min(r)
                u1 = max(r)
                ur.append(f'U+{u0:04X}{sep}{u1:04X}')
        if block_names:
            block_name = block_names.get(block_code, block_code).replace('_', ' ')
        else:
            block_name = ''
        print(f'{block_name}{prefix}' + ', '.join(ur) + suffix)


if __name__ == '__main__':
    main()
