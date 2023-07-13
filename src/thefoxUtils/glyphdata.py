#!/usr/bin/python3

import argparse
import csv
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser(description='Compare glyphnames')
    parser.add_argument('codepoints', help='list of codepoints')
    parser.add_argument('csv', help='CSV file of glyph names')
    parser.add_argument('xml', help='GlyphData.xml from GlyphsApp')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + '(The Fox Utils) ' + '23.6')
    args = parser.parse_args()

    codepoint_data = read_codepoints(args.codepoints)
    csv_data = read_csv(args.csv)
    xml_name_data, xml_altname_data = read_xml(args.xml)
    process(codepoint_data, csv_data, xml_name_data, xml_altname_data)


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


def process(codepoint_data, csv_data, xml_name_data, xml_altname_data):
    for codepoint in sorted(codepoint_data):
        usv = f'{codepoint:04X}'
        csv_name = csv_data.get(codepoint, 'lost')
        label = f'{usv}: {csv_name}'

        xml_name = xml_name_data.get(codepoint, 'xml_lost')
        xml_altname = xml_altname_data.get(codepoint, 'xmlalt_lost')
        if csv_name == xml_name:
            label += 'name'
        else:
            if csv_name == xml_altname:
                label += ' altname'
            else:
                label += ' GlyphsApp ' + xml_name  # + ' ' + xml_altname
        print(label)


if __name__ == '__main__':
    main()
