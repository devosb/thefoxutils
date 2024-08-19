#!/usr/bin/python3

import argparse
import lzma
import os
import os.path
import pickle

from thefoxUtils import version


def cmdline():
    parser = argparse.ArgumentParser(description='Show USV values of characters in a file')
    parser.add_argument('--count', help='count characters instead of just listing them',
                        action='store_true')
    parser.add_argument('--quote', help='quote a Unicode character')
    parser.add_argument('--encoding', help='file encoding',
                        default='utf-8')
    parser.add_argument('--errors', help='error mode for encoding',
                        default='strict')
    parser.add_argument('-o', '--octets', help='also display the bytes stored for each character',
                        action='store_true')
    parser.add_argument('-e', '--escape', help='output escaped text for use with FTML',
                        action='store_true')
    parser.add_argument('-p', '--python', help='output escaped text for use with Python',
                        action='store_true')
    parser.add_argument('--debug', help='display extra messages when reading a file',
                        action='store_true')
    parser.add_argument('-l', '--line', help='line number to start reading from',
                        type=int, default=1)
    parser.add_argument('-c', '--column', help='column number to start reading from',
                        type=int, default=1)
    parser.add_argument('--eol', help='read only to the end of the line',
                        action='store_true')
    parser.add_argument('--ucd', help='update the Unicode character database',
                        action='store_true')
    parser.add_argument('file', help='file to process', nargs='+')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + version)
    return parser


def main():
    parser = cmdline()
    args = parser.parse_args()
    ucdCacheFilename = os.path.join(os.environ["HOME"], ".unidump", "ucd.pickle.xz")

    if args.ucd:
        update_ucd(args.file, ucdCacheFilename)
    else:
        ucd = read_ucd(ucdCacheFilename)
        options = Options(args, ucd)
        if args.quote:
            quotechar(options)
        elif args.count:
            countfiles(options)
        else:
            dumpfiles(options)


class Options(object):

    def __init__(self, args, ucd):
        self.args = args
        self.ucd = ucd


def update_ucd(unicodeDataFilenames, ucdCacheFilename):
    """Update the Unicode Character Database (UCD) cache."""

    ucd = dict()
    for unicodeDataFilename in unicodeDataFilenames:
        with open(unicodeDataFilename) as unicodeDataFile:
            for line in unicodeDataFile:
                fields = line.split(';')
                usv = fields[0]
                name = fields[1]
                alt_name = fields[10]
                if name == '<control>':
                    name = f'({alt_name})'
                ucd[usv] = name
                if name.startswith('<') and name.endswith('First>'):
                    start = int(usv, 16)
                    name_pattern = name.strip('<>')
                    name_pattern = name_pattern.split(',')[0]
                if name.startswith('<') and name.endswith('Last>'):
                    stop = int(usv, 16)
                    for codepoint in range(start, stop + 1):
                        usv = codepoint2usv(codepoint)
                        name = f'{name_pattern}-{usv}'
                        ucd[usv] = name
    with lzma.open(ucdCacheFilename, 'wb') as ucdCacheFile:
        pickle.dump(ucd, ucdCacheFile)


def read_ucd(ucdCacheFile):
    """Read data from the Unicode Character Database (UCD) cache."""

    with lzma.open(ucdCacheFile, 'rb') as ucdCache:
        ucd = pickle.load(ucdCache)
    return ucd


def quotechar(options):
    """Show Unicode values for the character on the command line."""

    cc = usv2cc(options.args.quote)
    print(format(options, cc))


def dumpfiles(options):
    """Show Unicode values for the characters in the files."""

    for inputFilename in options.args.file:
        for display in dumpfile(options, inputFilename):
            print(formatoutput(options, display), end='')


def formatoutput(options, display):
    """Format contents of a file's output in a useful manor."""
    if options.args.python or options.args.escape:
        if display == '\\u000a':
            return '\n'
        else:
            return display
    else:
        return display + '\n'


def dumpfile(options, input_filename):
    """Show Unicode values for the characters in the file."""

    for cc in readfile(options, input_filename):
        display = format(options, cc)
        yield display


def countfiles(options):
    """Count characters in the files"""

    count = dict()
    for input_filename in options.args.file:
        countfile(options, count, input_filename)

    characters = sorted(count.keys())
    for cc in characters:
        display = "%7d %s" % (count[cc], format(options, cc))
        print(display)


def countfile(options, count, input_filename):
    """Count characters in the file"""

    for cc in readfile(options, input_filename):
        if cc in count:
            count[cc] += 1
        else:
            count[cc] = 1


def readfile(options, input_filename):
    """Return each character in the file, or requested subset of the file."""

    with open(input_filename, 'r', encoding=options.args.encoding, errors=options.args.errors, newline='') as input_file:
        lineno = 0
        columnno = 0
        for line in input_file:
            lineno = lineno + 1
            if options.args.debug:
                print("DEBUG: reading a line")
            if lineno < options.args.line:
                continue
            for i in range(len(line)):
                columnno = columnno + 1
                if columnno < options.args.column:
                    continue
                yield line[i]
            if options.args.eol:
                break


def format(options, cc):
    """Format the current character for display."""

    display = "%s %s" % (usv_format(cc), name_format(options, cc))
    if options.args.octets:
        # 19 characters is enough to display four bytes in hex with leading 0x's
        display = "%-19s %s" % (octets(options, cc), display)
    if options.args.python:
        # string literals do not need name or octets
        display = python(cc)
    if options.args.escape:
        # string literals do not need name or octets
        display = escape(cc)
    return display


def usv_format(cc):
    """Format the Unicode Scalar Value (USV) of the character."""
    return "U+{}".format(cc2usv(cc))


def name_format(options, cc):
    """Find name of the character."""
    usv = cc2usv(cc)
    return options.ucd.get(usv, "(Unknown)")


def usv2cc(usv):
    """Convert string USV to a character."""
    codepoint = int(usv, 16)
    return(chr(codepoint))


def cc2usv(cc):
    """Convert a character to a string of the USV."""
    return codepoint2usv(ord(cc))


def codepoint2usv(codepoint):
    """Convert a codepoint to a string of the USV."""
    return "%04X" % codepoint


def python(cc):
    """Format the character for a Python string."""
    codepoint = ord(cc)
    if 0x20 <= codepoint <= 0x7f:
        return cc
    if codepoint > 0xFFFF:
        return "\\U%08x" % codepoint
    return "\\u%04x" % codepoint


def escape(cc):
    """Format the character for a FTML string."""
    codepoint = ord(cc)
    if 0x20 <= codepoint <= 0x7f:
        return cc
    return "\\u%04x" % codepoint


def octets(options, cc):
    """Format each byte of the encoded character."""

    utf8_bytes = cc.encode(options.args.encoding)
    octets = []
    for utf8_byte in utf8_bytes:
        byte_in_hex = "0x%02X" % utf8_byte
        octets.append(byte_in_hex)
    return " ".join(octets)


if __name__ == "__main__":
    main()
