#!/usr/bin/python3

import argparse
import glob
import os.path

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

from thefoxUtils import version, unidump


def main():
    parser = argparse.ArgumentParser(description='Calculations for linespacing')
    parser.add_argument('test', help='directory of test data')
    parser.add_argument('fonts', help='fonts to read', nargs='+')
    parser.add_argument('-e', '--extra', help='extra directory of test data')
    parser.add_argument('--version', action='version', version='%(prog)s ' + version)
    args = parser.parse_args()

    test_words = find_words(args.test)
    test_words += find_words(args.extra)
    lowest_extremas, highest_extremas = find_extrema(test_words, args.fonts)
    report(lowest_extremas)
    report(highest_extremas)


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
        with open(os.path.join(test_dir, text_file), encoding='utf-8') as text:
            line_num = 0
            for line in text:
                words = line.split()
                word_num = 0
                for word in words:
                    test_word = TestWord(word, line_num, word_num, text_file)
                    test_words.append(test_word)
                    word_num += 1
                line_num += 1
    return test_words


def find_extrema(test_words, font_filenames):
    """Find extrema in TTF files"""

    lowest_extremas = []
    highest_extremas = []
    for font_filename in font_filenames:
        font = TTFont(font_filename)
        upem = font['head'].unitsPerEm
        lowest = upem
        highest = -upem
        glyph_set = font.getGlyphSet()
        bp = BoundsPen(glyph_set)

        hb_blob = hb.Blob.from_file_path(font_filename)
        hb_face = hb.Face(hb_blob)
        hb_font = hb.Font(hb_face)

        for test_word in test_words:
            buf = hb.Buffer()
            buf.add_str(test_word.text)
            buf.guess_segment_properties()
            features = {}
            hb.shape(hb_font, buf, features)
            infos = buf.glyph_infos
            positions = buf.glyph_positions
            for info, position in zip(infos, positions):
                gid = info.codepoint
                glyph_name = hb_font.glyph_to_string(gid)
                glyph = glyph_set[glyph_name]
                glyph.draw(bp)
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


def report(extremas):
    """Output information on extremas"""
    for extrema in extremas:
        print(extrema.report() + '\n')


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


if __name__ == '__main__':
    main()
