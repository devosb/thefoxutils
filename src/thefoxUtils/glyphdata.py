#!/usr/bin/python3

import xml.etree.ElementTree as ET
import fontParts.world as fontparts
import csv
import argparse


def main():
    parser = argparse.ArgumentParser(description='Compare glyph names')
    parser.add_argument('test', help='Test item to compare to reference')
    parser.add_argument('reference', help='Reference names to compare to')
    parser.add_argument('-f', '--filter', help='Only report on codepoints in filter')
    parser.add_argument('-r', '--report', help='Report on differences from the Glyphs.app XML file', action='store_true')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + '(The Fox Utils) ' + '23.6')
    args = parser.parse_args()

    test_data = reference_data = reference_alt_data = filter_data = None
    if args.test.endswith('.csv'):
        test_data = read_csv(args.test)
    if args.test.endswith('.ufo'):
        test_data = read_ufo(args.test)
    if args.reference.endswith('.xml'):
        reference_data, reference_alt_data = read_xml(args.reference)
    if args.reference.endswith('.csv'):
        reference_data = read_csv(args.reference)
    if args.filter:
        if args.filter.endswith('.txt'):
            filter_data = read_codepoints(args.filter)

    if args.report:
        report(filter_data, test_data, reference_data, reference_alt_data)
    else:
        output = rename(filter_data, test_data, reference_data)
        for line in output:
            print(line)


def codepoint2usv(codepoint):
    return f'{codepoint:06X}'


def read_codepoints(filename):
    data = list()
    with open(filename) as fh:
        for line in fh:
            # Ignore comments
            line = line.partition('#')[0]
            line = line.strip()

            # Ignore blank lines
            if line == '':
                continue

            # Convert data
            codepoint = int(line, 16)
            usv = codepoint2usv(codepoint)
            data.append(usv)
    return data


def read_csv(filename):
    data = dict()
    with open(filename, newline='') as fh:
        reader = csv.reader(fh)
        for row in reader:
            codepoint = int(row[0], 16)
            usv = codepoint2usv(codepoint)
            aglname = row[1]
            uniname = row[2]
            data[usv] = (aglname, uniname)
    return data


def read_ufo(filename):
    data = dict()
    rev_cmap = dict()
    font = fontparts.OpenFont(filename)
    for glyph in font:
        if glyph.unicode:
            base_glyph_name, dot, suffix = glyph.name.partition('.')
            usv = codepoint2usv(glyph.unicode)
            rev_cmap[f'{base_glyph_name}'] = usv
    for glyph in font:
        base_glyph_name, dot, suffix = glyph.name.partition('.')
        if base_glyph_name in rev_cmap:
            usv = rev_cmap[base_glyph_name]
            data[f'{glyph.name}'] = (glyph.name, 'UNI NAME', usv)
        else:
            data[f'{glyph.name}'] = (glyph.name, 'UNI NAME', '')
    return data


def read_xml(filename):
    name_data = dict()
    altname_data = dict()
    tree = ET.parse(filename)
    root = tree.getroot()
    for char in root:
        if 'unicode' in char.attrib:
            codepoint = int(char.attrib['unicode'], 16)
            usv = codepoint2usv(codepoint)
            name = char.attrib['name']
            uniname = char.attrib['description']
            name_data[usv] = (name, uniname, usv)

            if 'altNames' in char.attrib:
                altname = char.attrib['altNames']
                altname_data[usv] = (altname, uniname, usv)
    return name_data, altname_data


def report(filter_data, csv_data, xml_name_data, xml_altname_data):
    if filter_data:
        for filter in filter_data:
            if filter not in csv_data:
                print(f'missing filter {filter:04X}')

    for codepoint in sorted(csv_data):
        if filter_data and codepoint not in filter_data:
            if codepoint in ('0025CC',):
                pass
            else:
                continue
        # usv = f'{codepoint:04X}'
        usv = codepoint
        csv_name, uni_name = csv_data.get(codepoint, ('lost', 'LOST', ''))
        label = f'{usv},{csv_name},{uni_name},Glyphs.app:'

        xml_name, uni_name, usv = xml_name_data.get(codepoint, ('xml_lost', 'XML LOST', ''))
        xml_altname, uni_name, usv = xml_altname_data.get(codepoint, ('xmlalt_lost', 'XML ALT LOST', ''))
        if csv_name == xml_name:
            label += 'name'
        else:
            if csv_name == xml_altname:
                label += 'altname:' + xml_altname
            else:
                label += 'diff:' + xml_name
        print(label)
        # print(f'{usv},{csv_name},{uni_name}')


def rename(filter_data, ufo_data, csv_data):
    output = []
    for codepoint in sorted(ufo_data):
        if filter_data and codepoint not in filter_data:
            continue
        old_name, uni_name, usv = ufo_data.get(codepoint, (None, None, ''))
        old_base_name, dot, suffix = old_name.partition('.')
        new_name, uni_name, usv = csv_data.get(usv, (None, None, ''))
        if new_name is None:
            continue
        new_name = f'{new_name}{dot}{suffix}'
        if old_name != new_name:
            output.append(f'{old_name},{new_name}')
    return output


if __name__ == '__main__':
    main()
