#!/usr/bin/python3

import getopt
import sys
import os
import os.path

import re


def main():
    try:
        options = "c:e:hl:opv"
        long_options = ["column=", "count", "eol", "debug", "encoding=", "help", "line=", "octets", "python", "version"]
        opts, args = getopt.getopt(sys.argv[1:], options, long_options)
    except getopt.GetoptError:
        help()
        sys.exit(2)

    # option defaults
    mode = 'dump'
    debug = False
    encoding = "utf-8"
    show_octets = False
    python_escape = False
    line = 1
    column = 1
    stop = False

    for o, a in opts:
        if o in ("-c", "--column"):
            column = int(a)
        if o in "--eol":
            stop = True
        if o in "--count":
            mode = 'count'
        if o in "--debug":
            debug = True
        if o in ("-e", "--encoding"):
            encoding = a
        if o in ("-l", "--line"):
            line = int(a)
        if o in ("-o", "--octets"):
            show_octets = True
        if o in ("-p", "--python"):
            python_escape = True
        if o in ("-h", "--help"):
            help()
            sys.exit()
        if o in ("-v", "--version"):
            version(sys.argv[0])
            sys.exit()

    nameslist_file = os.path.join(os.environ["HOME"], ".unidump", "nameslist.lst")
    ucd = read_nameslist(nameslist_file)
    options = Options(mode, encoding, show_octets, python_escape, stop, debug, ucd)
    if mode == 'count':
        countfiles(options, args, line, column)
    else:
        dumpfiles(options, args, line, column)


def help():
    print("usage: unidump [--count] [-e|--encoding encoding] [-o|--octets] [-p|--python] [--debug] file1 file2 ...")
    print("  [-l|--line number] [-c|--column number] [--eol] file")
    print("values for encoding include ascii, cp*, iso8859_*, mac_*, utf_*, and others")

    # a full list of encodings and aliases is available
    # in the dictionary aliases in the file /usr/lib/python2.6/encodings/aliases.py
    # and on the web at http://docs.python.org/library/codecs.html#standard-encodings


def version(argv0):
    print("%s (%s) %s" % (argv0, 'The Fox Utils', '21.4'))


class Options(object):

    def __init__(self, mode, encoding, show_octets, python_escape, stop, debug, ucd):
        self.mode = mode
        self.encoding = encoding
        # self.nameslistFile = nameslist_file
        self.show_octets = show_octets
        self.python_escape = python_escape
        self.stop = stop
        self.debug = debug

        self.ucd = ucd
        # self.read_nameslist()

        self.count = dict()


def read_nameslist(nameslistFile):
    """Read data from customized nameslist file."""

    ucd = {}

    # Pre-populate ranges that are not in the nameslist file.
    cjk_ranges = (
        (0x4E00, 0x9FFC, ''),
        (0x3400, 0x4DBF, 'A'),
        (0x20000, 0x2A6DD, 'B'),
        (0x2A700, 0x2B734, 'C'),
        (0x2B740, 0x2B81D, 'D'),
        (0x2B820, 0x2CEA1, 'E'),
        (0x2CEB0, 0x2EBE0, 'F'),
        (0x30000, 0x3134A, 'G')
    )
    for cjk_range in cjk_ranges:
        start, end, label = cjk_range

        for usvOrd in range(start, end + 1):
            usv = codepoint2usv(usvOrd)
            name = 'CJK Unified Ideograph'
            if label != '':
                name = ' '.join([name, 'Ext', label])
            ucd[usv] = '{}-{}'.format(name, usv)

    # Read nameslist file.
    nameslist = open(nameslistFile, 'r')
    re_usv_and_name = re.compile("([\dA-F]+)\t([\w\- <>]+)")
    re_alt_name = re.compile("\t= ([\w\- \(\),]+)")
    usv = ""
    name = ""
    for line in nameslist:
        m = re_usv_and_name.match(line)
        if m:
            usv = m.group(1)
            name = m.group(2)

        if name == "<control>":
            m = re_alt_name.match(line)
            if m:
                alt_name = m.group(1)
                name = "(%s)" % alt_name

        ucd[usv] = name
    nameslist.close()

    # Populate additional ranges that are not in the nameslist file.
    for usvOrd in range(0xD800, 0xDB7F):
        usv = codepoint2usv(usvOrd)
        ucd[usv] = "(High Surrogate)"

    for usvOrd in range(0xDB80, 0xDBFF):
        usv = codepoint2usv(usvOrd)
        ucd[usv] = "(High Private Use Surrogate)"

    for usvOrd in range(0xDC00, 0xDFFF):
        usv = codepoint2usv(usvOrd)
        ucd[usv] = "(Low Surrogate)"

    return ucd


def dumpfiles(options, input_filenames, start_line, start_column):
    """Show Unicode values for the characters in the files."""

    for inputFilename in input_filenames:
        for display in dumpfile(options, inputFilename, start_line, start_column):
            print(formatoutput(options, display), end='')


def formatoutput(options, display):
    """Format contents of a file's output in a useful manor."""
    if options.python_escape:
        if display == '\\u000a':
            return '\n'
        else:
            return display
    else:
        return display + '\n'


def dumpfile(options, input_filename, start_line, start_column):
    """Show Unicode values for the characters in the file."""

    for cc in readfile(options, input_filename, start_line, start_column):
        display = format(options, cc)
        yield display


def countfiles(options, input_filenames, start_line, start_column):
    """Count characters in the files"""

    for input_filename in input_filenames:
        countfile(options, input_filename, start_line, start_column)

    characters = sorted(options.count.keys())
    for cc in characters:
        display = "%7d %s" % (options.count[cc], format(options, cc))
        print(display)


def countfile(options, input_filename, start_line, start_column):
    """Count characters in the file"""

    for cc in readfile(options, input_filename, start_line, start_column):
        if cc in options.count:
            options.count[cc] += 1
        else:
            options.count[cc] = 1


def readfile(options, input_filename, start_line, start_column):
    """Return each character in the file, or requested subset of the file."""

    with open(input_filename, 'r', newline='') as input_file:
        lineno = 0
        columnno = 0
        for line in input_file:
            lineno = lineno + 1
            if options.debug:
                print("DEBUG: reading a line")
            if lineno < start_line:
                continue
            for i in range(len(line)):
                columnno = columnno + 1
                if columnno < start_column:
                    continue
                yield line[i]
            if options.stop:
                break


def format(options, cc):
    """Format the current character for display."""

    display = "%s %s" % (usv_format(cc), name_format(options, cc))
    if options.show_octets:
        # 19 characters is enough to display four bytes in hex with leading 0x's
        display = "%-19s %s" % (octets(options, cc), display)
    if options.python_escape:
        # string literals do not need name or octets
        display = python(cc)
    return display


def usv_format(cc):
    """Format the Unicode Scalar Value (USV) of the character."""
    return "U+{}".format(cc2usv(cc))


def name_format(options, cc):
    """Find name of the character."""
    usv = cc2usv(cc)
    return options.ucd.get(usv, "(Unknown)")


def cc2usv(cc):
    """Convert a character to a string of the USV."""
    return codepoint2usv(ord(cc))


def codepoint2usv(codepoint):
    """Convert a character to a string of the USV."""
    return "%04X" % codepoint


def python(cc):
    """Format the character for a Python string."""
    codepoint = ord(cc)
    if 0x20 <= codepoint <= 0x7f:
        return cc
    if codepoint > 0xFFFF:
        return "\\U%08x" % codepoint
    return "\\u%04x" % codepoint


def octets(options, cc):
    """Format each byte of the encoded character."""

    utf8_bytes = cc.encode(options.encoding)
    octets = []
    for utf8_byte in utf8_bytes:
        byte_in_hex = "0x%02X" % utf8_byte
        octets.append(byte_in_hex)
    return " ".join(octets)


if __name__ == "__main__":
    main()
