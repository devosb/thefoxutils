#!/usr/bin/python3

import argparse
import csv

parser = argparse.ArgumentParser()
# parser.add_argument("-a", "--album", help="name of album to place into")
parser.add_argument("files", help="files to read", nargs="*")
parser.add_argument("--version", action="version", version="%(prog)s 0.1")
args = parser.parse_args()


def main():
    """Process UnicodeData.txt files."""
    spreadsheet = csv.writer(open('spreadsheet.csv', 'w'), quoting=csv.QUOTE_ALL)
    pynameslist = open('pynameslist.txt', 'w')
    pyfontaine = open('pyfontaine.txt', 'w')
    quote = open('quote.txt', 'w')

    for filename in args.files:
        unicodedata = csv.reader(open(filename), delimiter=';')
        for line in unicodedata:
            # read Unicode data
            usv = line[0]
            name = line[1]

            # create modified data
            charset = '    0x{},  # {}\n'.format(usv, name)
            decimal = int(usv, 16)
            # glyph = '  {0} '.format(chr(decimal))
            glyph = '  x '
            copy_paste = 'U+{} {}\n'.format(usv, name)

            # output various formats
            spreadsheet.writerow([usv, decimal, glyph, name])
            pynameslist.write(charset)
            pyfontaine.write('    ' + charset)
            quote.write(copy_paste)


if __name__ == "__main__":
    main()
