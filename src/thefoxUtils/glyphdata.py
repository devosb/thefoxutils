#!/usr/bin/python3

import xml.etree.ElementTree as ET
from fontParts.world import *
import csv
import argparse


def main():
    parser = argparse.ArgumentParser(description='Compare glyph names')
    parser.add_argument('test', help='Test item to compare to reference')
    parser.add_argument('reference', help='Reference names to compare to')
    parser.add_argument('-f', '--filter', help='Only report on codepoints in filter')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + '(The Fox Utils) ' + '23.6')
    args = parser.parse_args()

    report_mode = False
    test_data = reference_data = reference_alt_data = filter_data = None
    if args.test.endswith('.csv'):
        test_data = read_csv(args.test)
    if args.test.endswith('.ufo'):
        test_data = read_ufo(args.test)
    if args.reference.endswith('.xml'):
        reference_data, reference_alt_data = read_xml(args.reference)
        report_mode = True
    if args.reference.endswith('.csv'):
        reference_data = read_csv(args.reference)
    if args.filter:
        if args.filter.endswith('.txt'):
            filter_data = read_codepoints(args.filter)

    if report_mode:
        report(filter_data, test_data, reference_data, reference_alt_data)
    else:
        rename(filter_data, test_data, reference_data)


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
            data.append(codepoint)
    return data


def read_csv(filename):
    data = dict()
    with open(filename, newline='') as fh:
        reader = csv.reader(fh)
        for row in reader:
            codepoint = int(row[0], 16)
            name = row[1]
            data[codepoint] = name
    return data


def read_ufo(filename):
    data = dict()
    font = OpenFont(filename)
    for glyph in font:
        if glyph.unicode:
            glyph_name = glyph.name
            data[glyph.unicode] = glyph_name
    return data


def read_xml(filename):
    name_data = dict()
    altname_data = dict()
    tree = ET.parse(filename)
    root = tree.getroot()
    for char in root:
        if 'unicode' in char.attrib:
            codepoint = int(char.attrib['unicode'], 16)
            name = char.attrib['name']
            name_data[codepoint] = name

            if 'altNames' in char.attrib:
                altname = char.attrib['altNames']
                altname_data[codepoint] = altname
    return name_data, altname_data


def report(filter_data, csv_data, xml_name_data, xml_altname_data):
    for codepoint in sorted(csv_data):
        if filter_data and codepoint not in filter_data:
            continue
        usv = f'{codepoint:04X}'
        csv_name = csv_data.get(codepoint, 'lost')
        label = f'{usv}: {csv_name} '

        xml_name = xml_name_data.get(codepoint, 'xml_lost')
        xml_altname = xml_altname_data.get(codepoint, 'xmlalt_lost')
        if csv_name == xml_name:
            label += 'name'
        else:
            if csv_name == xml_altname:
                label += 'altname'
            else:
                label += 'Glyphs.app ' + xml_name  # + ' ' + xml_altname
        print(label)


def rename(filter_data, ufo_data, csv_data):
    for codepoint in sorted(ufo_data):
        if filter_data and codepoint not in filter_data:
            continue
        old_name = ufo_data.get(codepoint)
        new_name = csv_data.get(codepoint)
        if new_name == None:
            continue
        if old_name != new_name:
            print(f'{old_name},{new_name}')


if __name__ == '__main__':
    main()
