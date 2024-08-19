#!/usr/bin/python3

import argparse
import os.path
import re

from thefoxUtils import version


def main():
    parser = argparse.ArgumentParser(description='Produce literal text from escaped text')
    parser.add_argument('-o', '--output', help='output file')
    parser.add_argument('file', help='File to process', nargs='+')
    parser.add_argument('--version', action='version', version='%(prog)s ' + version)
    args = parser.parse_args()

    if args.output:
        create(args.output, args.file)
    else:
        for input_filename in args.file:
            (root, ext) = os.path.splitext(input_filename)
            output_filename = f'{root}.txt'
            create(output_filename, [input_filename])


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
