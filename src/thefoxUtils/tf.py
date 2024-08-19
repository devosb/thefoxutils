#!/usr/bin/python3

import argparse
import os
import unicodedata

from thefoxUtils import version

# from palaso.teckit import engine

DOS = '\r\n'
MAC = '\r'
UNIX = '\n'


def main():
    parser = argparse.ArgumentParser(description='Report on and optionally change text files')
    parser.add_argument('-d', '--dos', action='store_const', const=DOS,
                        dest='requested_eol', help='convert to DOS format')
    parser.add_argument('-m', '--mac', action='store_const', const=MAC,
                        dest='requested_eol', help='convert to MAC format')
    parser.add_argument('-u', '--unix', action='store_const', const=UNIX,
                        dest='requested_eol', help='convert to UNIX format')
    parser.add_argument('--nfc', action='store_const', const='NFC',
                        dest='requested_nf', help='apply NFC normalization')
    parser.add_argument('--nfd', action='store_const', const='NFD',
                        dest='requested_nf', help='apply NFD normalization')
    parser.add_argument('-w', '--whitespace', action='store_true',
                        help='trim trailing whitespace')
    parser.add_argument('file', help='files to process', nargs='+')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + version)
    args = parser.parse_args()

    process_files(args)


def normalize(form, text):
    """Return the normal form form for the Unicode string unistr.

    Valid values for form are 'NFC', 'NFKC', 'NFD', and 'NFKD'.
    """
    return unicodedata.normalize(form, text)


def process_files(args):
    max_filename_length = 0
    for input_filename in args.file:
        max_filename_length = max(len(input_filename), max_filename_length)
    for input_filename in args.file:
        filename = '{:{width}s}'.format(input_filename, width=max_filename_length)
        reports = process_file(args.requested_eol, args.requested_nf, args.whitespace, input_filename)
        sep = ':'
        if reports != '':
            sep += ' '
        print(f'{filename}{sep}{reports}')


def process_file(requested_eol, normalization, whitespace, input_filename):
    input_file = open(input_filename, 'r', encoding='utf-8', newline='')

    if requested_eol or whitespace or normalization:
        # TODO use module tempfile
        temp_filename = input_filename + '.temp'
        temp = open(temp_filename, 'w', encoding='utf-8')

    # run through all the lines in the file
    newlines = set()
    trailing_eol = True
    trailing_whitespace = False
    blank_line = False
    nfc = True
    nfd = True
    for line in input_file:
        # find out what type of newline there is
        if line.endswith(DOS):
            current_eol = DOS
            label = 'dos'
        elif line.endswith(MAC):
            current_eol = MAC
            label = 'mac'
        elif line.endswith(UNIX):
            current_eol = UNIX
            label = 'unix'
        else:
            current_eol = ''
            label = 'missing'
            trailing_eol = False
        newlines.add(label)
        all_text = line.rstrip(current_eol)

        # remove trailing whitespace from the line
        visible_text = all_text.rstrip(' \t')
        if visible_text == '':
            blank_line = True
        else:
            blank_line = False
        if all_text != visible_text:
            trailing_whitespace = True
        if whitespace:
            all_text = visible_text

        # normalize text
        if all_text != normalize('NFC', all_text):
            nfc = False
        if all_text != normalize('NFD', all_text):
            nfd = False
        if normalization:
            all_text = normalize(normalization, all_text)

        # change eol in the file
        if requested_eol:
            current_eol = requested_eol
        output_line = all_text + current_eol

        if requested_eol or whitespace or normalization:
            # write line and new eol and any trimmed whitespace to a temp file
            temp.write(output_line)

    # report on what was found in the file
    reports = list()

    # newlines

    # full report
    if not trailing_eol:
        newlines.discard('missing')
    nl = sorted(newlines)
    if not trailing_eol:
        nl.append('missing')

    # condensed report
    if len(nl) == 1 and 'unix' in nl:
        pass
    else:
        nl_report = 'nl: ' + ' '.join(nl)
        reports.append(nl_report)

    # normalization forms

    # full report
    nf = list()
    nf_report = 'nf:'
    if nfc:
        nf.append('c')
    if nfd:
        nf.append('d')

    # condensed report
    if nfc and nfd:
        pass
    elif len(nf) > 0:
        nf_report += ' ' + ' '.join(nf)
        reports.append(nf_report)
    else:
        reports.append(nf_report)

    # whitespace

    # full report
    ws = list()
    if trailing_whitespace:
        ws.append('eol')
    if blank_line:
        ws.append('eof')

    # condensed report
    if len(ws) > 0:
        ws_report = 'ws: ' + ' '.join(ws)
        reports.append(ws_report)

    # cleanup
    input_file.close()
    if requested_eol or whitespace or normalization:
        temp.close()

        cmd = "touch -r \"%s\" \"%s\"" % (input_filename, temp_filename)
        os.system(cmd)
        os.remove(input_filename)
        os.rename(temp_filename, input_filename)

    # output
    return ' '.join(reports)


if __name__ == '__main__':
    main()
