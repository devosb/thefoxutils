#!/usr/bin/python3

import argparse
import glob
import os.path

import tabulate
import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont
import fontParts.world as fontparts

from thefoxUtils import version, unidump


def main():
    parser = argparse.ArgumentParser(description='Calculations for linespacing')
    parser.add_argument('fonts', help='fonts to read', nargs='+')
    parser.add_argument('-t', '--test', help='directory of test data (repeatable)', action='append')
    parser.add_argument('-n', '--records', help='output last number of extrema', default=10, type=int)
    parser.add_argument('--version', action='version', version='%(prog)s ' + version)
    args = parser.parse_args()

    test_words = []
    if args.test:
        for test_dir in args.test:
            test_words += find_words(test_dir)
    lowest_extremas, highest_extremas = find_extrema(test_words, args.fonts)
    report(lowest_extremas, args.records)
    report(highest_extremas, args.records)
    show(lowest_extremas, highest_extremas, args.fonts)


class TestWord():
    """Test word"""

    def __init__(self, text, line_num, word_num, text_filename):
        self.text = text
        self.line_num = line_num
        self.word_num = word_num
        self.text_filename = text_filename


def find_words(test_dir):
    """Make a list of words from the text"""

    if not test_dir:
        return []
    test_words = []
    text_files = glob.glob('**/*.*txt', root_dir=test_dir, recursive=True)
    for text_file in text_files:
        print(f'Reading {text_file}')
        with open(os.path.join(test_dir, text_file), encoding='utf-8') as text:
            line_num = 1
            for line in text:
                words = line.split()
                word_num = 1
                for word in words:
                    test_word = TestWord(word, line_num, word_num, text_file)
                    test_words.append(test_word)
                    word_num += 1
                line_num += 1
    return test_words


def find_extrema(test_words, font_filenames):
    """Find extrema in TTF files"""

    if not test_words:
        return [], []
    lowest_extremas = []
    highest_extremas = []
    lowest = 1000
    highest = -1000
    for font_filename in font_filenames:
        root, ext = os.path.splitext(font_filename)
        if ext == '.ufo':
            continue
        print(f'Processing {font_filename}')
        font = TTFont(font_filename)

        hb_blob = hb.Blob.from_file_path(font_filename)
        hb_face = hb.Face(hb_blob)
        hb_font = hb.Font(hb_face)

        text_file = ''
        for test_word in test_words:
            if test_word.text_filename != text_file:
                print(f'Shaping {test_word.text_filename}')
                text_file = test_word.text_filename
            buf = hb.Buffer()
            buf.add_str(test_word.text)
            buf.guess_segment_properties()
            features = {}
            hb.shape(hb_font, buf, features)
            infos = buf.glyph_infos
            positions = buf.glyph_positions
            for info, position in zip(infos, positions):
                glyph_set = font.getGlyphSet()
                bp = BoundsPen(glyph_set)
                gid = info.codepoint
                glyph_name = hb_font.glyph_to_string(gid)
                glyph = glyph_set[glyph_name]
                glyph.draw(bp)
                if bp.bounds is None:
                    continue
                (xmin, ymin, xmax, ymax) = bp.bounds
                y_offset = position.y_offset
                low = ymin + y_offset
                high = ymax + y_offset
                if low < lowest:
                    lowest = low
                    lowest_extremas = []
                if low == lowest:
                    extrema = Extrema(test_word, low, font_filename)
                    lowest_extremas.append(extrema)
                if high > highest:
                    highest = high
                    highest_extremas = []
                if high == highest:
                    extrema = Extrema(test_word, high, font_filename)
                    highest_extremas.append(extrema)
    return lowest_extremas, highest_extremas


def report(extremas, records):
    """Output information on extremas"""
    count = 1
    for extrema in extremas:
        print(extrema.report() + '\n')
        count += 1
        if count > records:
            break


class Extrema:
    """Data about an extrema"""

    def __init__(self, test_word, level, font_filename):
        self.test_word = test_word
        self.level = level
        self.font_filename = font_filename

    def report(self):
        escape = ''
        for char in self.test_word.text:
            escape += unidump.escape(char)
        return f'{self.test_word.text}\n{escape}\nat {self.level} from {self.test_word.text_filename}:{self.test_word.line_num}:{self.test_word.word_num} in {self.font_filename}'


def show(lowest, highest, fonts):
    data = []

    high_labels = [
        'ascender', 'OS2WinAscent', 'OS2TypoAscender', 'HheaAscender',
    ]
    if highest:
        high_labels.append('HIGHEST')

    low_labels = [
        'descender', 'OS2WinDescent (-)', 'OS2TypoDescender', 'HheaDescender',
    ]
    if lowest:
        low_labels.append('LOWEST')

    other_labels = [
        'OS2TypoLineGap', 'HheaLineGap'
    ]
    labels = high_labels + low_labels + other_labels
    if len(fonts) > 1:
        labels.insert(0, 'Field')
    data.append(labels)

    align = ['left']
    for font_filename in fonts:
        root, ext = os.path.splitext(font_filename)
        if ext == '.ufo':
            font = fontparts.OpenFont(font_filename)

            high_values = [
                font.info.ascender,
                font.info.openTypeOS2WinAscent,
                font.info.openTypeOS2TypoAscender,
                font.info.openTypeHheaAscender,
            ]
            low_values = [
                font.info.descender,
                -font.info.openTypeOS2WinDescent,
                font.info.openTypeOS2TypoDescender,
                font.info.openTypeHheaDescender,
            ]
            other_values = [
                font.info.openTypeOS2TypoLineGap,
                font.info.openTypeHheaLineGap
            ]

        else:
            font = TTFont(font_filename)

            high_values = [
                '',
                font['OS/2'].usWinAscent,
                font['OS/2'].sTypoAscender,
                font['hhea'].ascender,
            ]
            low_values = [
                '',
                -font['OS/2'].usWinDescent,
                font['OS/2'].sTypoDescender,
                font['hhea'].descender,
            ]
            other_values = [
                font['OS/2'].sTypoLineGap,
                font['hhea'].lineGap
            ]

        if highest:
            high_values.append(highest[0].level) 
        if lowest:
            low_values.append(lowest[0].level)
        values = high_values + low_values + other_values
        if len(fonts) > 1:
            values.insert(0, root)
        align.append('right')
        data.append(values)

    output = tabulate.tabulate(zip(*data), tablefmt='plain', colalign=align)
    print(output)


if __name__ == '__main__':
    main()
