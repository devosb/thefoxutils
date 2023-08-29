#!/usr/bin/python3

import os
import unittest

from thefoxUtils import unidump


class UnidumpTests(unittest.TestCase):

    def setUp(self):
        os.chdir('tests/data/unidump')
        ucd = unidump.read_ucd("ucd.pickle.xz")
        parser = unidump.cmdline()
        args = parser.parse_args(["position.txt"])
        self.options = unidump.Options(args, "dump", "utf_8", False, False, False, False, ucd)

    def tearDown(self):
        os.chdir('../../..')

    # The two ignored tests pass on Ubuntu 9.04 with Python 2.6,
    # but fails on Windows XP with ActiveState Python 2.6.2.2.
    # Difference is probably the Python interperter storing Unicode strings as UTF-16 or UTF-32.
    # With UTF-16 a non plane 0 character will return two characters from the ord() call.

    # dump file position

    def test_posStart(self):
        self.assertEqual("U+0031 DIGIT ONE", next(unidump.dumpfile(self.options, "position.txt", 1, 1)))

    def test_posLine(self):
        self.assertEqual("U+0032 DIGIT TWO", next(unidump.dumpfile(self.options, "position.txt", 2, 1)))

    def test_posLineColumn(self):
        self.assertEqual("U+0034 DIGIT FOUR", next(unidump.dumpfile(self.options, "position.txt", 4, 6)))

    # count

    def test_countFile(self):
        unidump.countfile(self.options, "position.txt", 1, 1)
        self.assertEqual(2, self.options.count['1'], 'one')
        self.assertEqual(2, self.options.count['4'], 'four')
        self.assertEqual(3, self.options.count['e'], 'letter e')

    def test_countFiles(self):
        # this displays the output
        # unidump.countfiles(self.options, ["position.txt", "position.txt"], 1, 1)

        # does not display the output, but does tests a (slightly) different function
        unidump.countfile(self.options, "position.txt", 1, 1)
        unidump.countfile(self.options, "position.txt", 1, 1)

        self.assertEqual(4, self.options.count['1'], 'one')
        self.assertEqual(4, self.options.count['4'], 'four')
        self.assertEqual(6, self.options.count['e'], 'letter e')

    # usv

    def test_usvLatin1(self):
        self.assertEqual("U+00F1", unidump.usv_format("\u00F1"))

    def test_usvPlane1(self):
        self.assertEqual("U+1D510", unidump.usv_format("\U0001D510"))

    # python

    def test_pythonASCII(self):
        self.assertEqual("A", unidump.python("A"))

    def test_pythonLatin1(self):
        self.assertEqual("\\u00f1", unidump.python("\u00F1"))

    def test_python1252(self):
        self.assertEqual("\\u0161", unidump.python("\u0161"))

    def test_pythonPlane1(self):
        self.assertEqual("\\U0001d510", unidump.python("\U0001D510"))

    def test_pythonNewline(self):
        self.assertEqual("\\u000a", unidump.python("\n"))

    # escape

    def test_escapeASCII(self):
        self.assertEqual("A", unidump.escape("A"))

    def test_escapeLatin1(self):
        self.assertEqual("\\u00f1", unidump.escape("\u00F1"))

    def test_escape1252(self):
        self.assertEqual("\\u0161", unidump.escape("\u0161"))

    def test_escapePlane1(self):
        self.assertEqual("\\u1d510", unidump.escape("\U0001D510"))

    def test_escapeNewline(self):
        self.assertEqual("\\u000a", unidump.escape("\n"))

    # name

    def test_nameControl(self):
        self.assertEqual("(LINE FEED (LF))", unidump.name_format(self.options, "\u000A"))

    def test_nameLatin1(self):
        self.assertEqual("LATIN SMALL LETTER N WITH TILDE", unidump.name_format(self.options, "\u00F1"))

    def test_nameChineseAlast(self):
        self.assertEqual("CJK Ideograph Extension A-4DBF", unidump.name_format(self.options, "\u4DBF"))

    def test_nameChineseURO(self):
        self.assertEqual("CJK Ideograph-6606", unidump.name_format(self.options, "\u6606"))

    def test_nameChineseUROlast(self):
        self.assertEqual("CJK Ideograph-9FFC", unidump.name_format(self.options, "\u9FFC"))

    def test_nameChineseB(self):
        self.assertEqual("CJK Ideograph Extension B-20040", unidump.name_format(self.options, "\U00020040"))

    def test_nameChineseBlast(self):
        self.assertEqual("CJK Ideograph Extension B-2A6DD", unidump.name_format(self.options, "\U0002A6DD"))

    def test_nameChineseClast(self):
        self.assertEqual("CJK Ideograph Extension C-2B739", unidump.name_format(self.options, "\U0002B739"))

    def test_nameChineseDlast(self):
        self.assertEqual("CJK Ideograph Extension D-2B81D", unidump.name_format(self.options, "\U0002B81D"))

    def test_nameChineseE(self):
        self.assertEqual("CJK Ideograph Extension E-2CA62", unidump.name_format(self.options, "\U0002CA62"))

    def test_nameChineseElast(self):
        self.assertEqual("CJK Ideograph Extension E-2CEA1", unidump.name_format(self.options, "\U0002CEA1"))

    def test_nameChineseFlast(self):
        self.assertEqual("CJK Ideograph Extension F-2EBE0", unidump.name_format(self.options, "\U0002EBE0"))

    def test_nameChineseGlast(self):
        self.assertEqual("CJK Ideograph Extension G-3134A", unidump.name_format(self.options, "\U0003134A"))

    def test_nameChineseHlast(self):
        self.assertEqual("CJK Ideograph Extension H-323AF", unidump.name_format(self.options, "\U000323AF"))

    def test_nameBranchPUA(self):
        self.assertEqual("BRANCH PUA-E000", unidump.name_format(self.options, "\uE000"))

    def test_nameMicrosoftPUA(self):
        self.assertEqual("MICROSOFT PUA-F000", unidump.name_format(self.options, "\uF000"))

    def test_nameSilPUA(self):
        self.assertEqual("SIL PUA-F130", unidump.name_format(self.options, "\uF130"))

    def test_nameBOM(self):
        self.assertEqual("ZERO WIDTH NO-BREAK SPACE", unidump.name_format(self.options, "\uFEFF"))

    def test_namePlane1(self):
        self.assertEqual("MATHEMATICAL FRAKTUR CAPITAL M", unidump.name_format(self.options, "\U0001D510"))

    # Since the previous test fails, we need to be able to show names for surrogate pairs
    def test_nameHighSurrogate(self):
        self.assertEqual("Non Private Use High Surrogate-D800", unidump.name_format(self.options, "\uD800"))

    def test_nameHighPrivateUseSurrogate(self):
        self.assertEqual("Private Use High Surrogate-DB80", unidump.name_format(self.options, "\uDB80"))

    def test_nameLowSurrogate(self):
        self.assertEqual("Low Surrogate-DC00", unidump.name_format(self.options, "\uDC00"))

    # octets

    def test_octetsControl(self):
        self.assertEqual("0x0A", unidump.octets(self.options, "\u000A"))

    def test_octetsLatin1(self):
        self.assertEqual("0xC3 0xB1", unidump.octets(self.options, "\u00F1"))

    def test_octetsBOM(self):
        self.assertEqual("0xEF 0xBB 0xBF", unidump.octets(self.options, "\uFEFF"))

    def test_octetsPlane1(self):
        self.assertEqual("0xF0 0x9D 0x94 0x90", unidump.octets(self.options, "\U0001D510"))


if __name__ == "__main__":
    unittest.main()
