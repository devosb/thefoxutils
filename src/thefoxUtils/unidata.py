#!/usr/bin/python3

import argparse
import csv

from thefoxUtils import version

parser = argparse.ArgumentParser()
parser.add_argument("files", help="files to read", nargs="*")
parser.add_argument('--version', action='version', version='%(prog)s ' + version)
args = parser.parse_args()


def main():
    """Process UnicodeData.txt files."""
    spreadsheet = csv.writer(open('spreadsheet.csv', 'w'), quoting=csv.QUOTE_ALL)
    pyfontaine = open('pyfontaine.txt', 'w')
    quote = open('quote.txt', 'w')

    for filename in args.files:
        unicodedata = csv.reader(open(filename), delimiter=';')
        for line in unicodedata:
            # read Unicode data
            usv = line[0]
            name = line[1]

            # create modified data
            charset = f'        0x{usv},  # {name}\n'
            decimal = int(usv, 16)
            # glyph = '  {0} '.format(chr(decimal))
            glyph = '  x '
            copy_paste = 'U+{} {}\n'.format(usv, name)

            # output various formats
            spreadsheet.writerow([usv, decimal, glyph, name])
            pyfontaine.write(charset)
            quote.write(copy_paste)


if __name__ == "__main__":
    main()
