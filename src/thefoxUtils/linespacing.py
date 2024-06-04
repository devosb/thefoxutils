#!/usr/bin/python3

import argparse

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

from thefoxUtils import unidump


def main():
    parser = argparse.ArgumentParser(description='Calculations for linespacing')
    parser.add_argument('text', help='text file of test data')
    parser.add_argument('fonts', help='fonts to read', nargs='+')
    args = parser.parse_args()

    words = find_words(args.text)
    lowest_extremas, highest_extremas = find_extrema(words, args.fonts)
    report(lowest_extremas)
    report(highest_extremas)


def find_words(text_file):
    """Make a list of words from the text"""

    word_list = []
    with open(text_file) as text:
        for line in text:
            words = line.split()
            for word in words:
                word_list.append(word)
    return word_list


def find_extrema(words, font_filenames):
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

        for word in words:
            buf = hb.Buffer()
            buf.add_str(word)
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
                low = ymin+y_offset
                high = ymax+y_offset
                if low < lowest:
                    lowest = low
                    lowest_extremas = []
                if low == lowest:
                    extrema = Extrema(word, low, font_filename)
                    lowest_extremas.append(extrema)
                if high > highest:
                    highest = high
                    highest_extremas = []
                if high == highest:
                    extrema = Extrema(word, high, font_filename)
                    highest_extremas.append(extrema)
    return lowest_extremas, highest_extremas


def report(extremas):
    """Output information on extremas"""
    for extrema in extremas:
        print(extrema.report() + '\n')


class Extrema():
    """Data about an extrema"""

    def __init__(self, word, level, font_filename):
        self.word = word
        self.level = level
        self.font_filename = font_filename

    def report(self):
        escape = ''
        for char in self.word:
            escape += unidump.escape(char)
        return f'{self.word}\n{escape}\nat {self.level} in {self.font_filename}'


if __name__ == '__main__':
    main()
