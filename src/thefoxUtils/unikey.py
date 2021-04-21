#!/usr/bin/python3

import re
import getopt
import sys


def main():
    try:
        options = "ho:v"
        long_options = ["help", "output=", "version"]
        opts, args = getopt.getopt(sys.argv[1:], options, long_options)
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    output_filename = ""
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-o", "--output"):
            output_filename = a
        if o in ("-v", "--version"):
            version()
            sys.exit()

    create(output_filename, args)


def usage():
    print("usage: unikey -o|--output file.txt file.htxt")


def version():
    print("unikey version 1.1")


def literal2char(literal):
    """Convert a string literal to the actual character."""
    usv = literal.group(1)
    codepoint = int(usv, 16)
    char = chr(codepoint)
    return char


def modify(literal_text):
    """Replace character literals with the actual characters."""
    literals = r'\\[uU]([0-9A-Fa-f]+)'
    actual_text = re.sub(literals, literal2char, literal_text)
    return actual_text


def create(output_filename, files):
    """Write Unicode characters to the file."""
    output_file = open(output_filename, 'w')
    for input_filename in files:
        input_file = open(input_filename, 'r')
        for line in input_file:
            line = modify(line)
            output_file.write(line)


if __name__ == "__main__":
    main()
