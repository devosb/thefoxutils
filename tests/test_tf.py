#!/usr/bin/python3

import os
import sys
import unittest

from thefoxUtils import tf


class TextFileTests(unittest.TestCase):

    def setUp(self):
        os.chdir('tests/data/tf')
        self.version = sys.version_info

    def tearDown(self):
        os.chdir('../../..')

    # Line endings

    def test_dos(self):
        filename = 'dos.rawtxt'
        self.assertEqual('nl: dos ws: eol', tf.process_file(None, None, None, filename))

    def test_mac(self):
        filename = 'mac.rawtxt'
        self.assertEqual('nl: mac', tf.process_file(None, None, None, filename))

    def test_unix(self):
        filename = 'unix.rawtxt'
        self.assertEqual('ws: eol eof', tf.process_file(None, None, None, filename))

    def test_missing_dos(self):
        filename = 'missing-dos.rawtxt'
        self.assertEqual('nl: dos missing ws: eol', tf.process_file(None, None, None, filename))

    def test_missing_unix(self):
        filename = 'missing-unix.rawtxt'
        self.assertEqual('nl: unix missing ws: eol', tf.process_file(None, None, None, filename))

    def test_changeOS(self):
        filename = 'change_os.rawtxt'
        self.assertEqual('nl: dos unix ws: eof', tf.process_file(None, None, None, filename))

    # Normalization forms

    def helper_nf(self, expected):
        if sys.platform.startswith('win'):
            dos = 'nl: dos'
            if expected == '':
                return dos
            else:
                return dos + ' ' + expected
        else:
            return expected

    def test_nf_c(self):
        filename = 'nf-c.txt'
        self.assertEqual(self.helper_nf('nf: c'), tf.process_file(None, None, None, filename))

    def test_nf_d(self):
        filename = 'nf-d.txt'
        self.assertEqual(self.helper_nf('nf: d'), tf.process_file(None, None, None, filename))

    def test_nf_both(self):
        filename = 'nf-both.txt'
        self.assertEqual(self.helper_nf(''), tf.process_file(None, None, None, filename))

    def test_nf_none(self):
        filename = 'nf-none.txt'
        self.assertEqual(self.helper_nf('nf:'), tf.process_file(None, None, None, filename))

    def test_nfc_tus1(self):
        text = u'e\u0301'
        self.assertEqual(u'\u00e9', tf.normalize('NFC', text))

    def test_nfd_tus1(self):
        text = u'\u00e9'
        self.assertEqual(u'e\u0301', tf.normalize('NFD', text))

    def test_nfc_tus10(self):
        if self.version.minor < 7:
            return
        text = u'\u0061\u035C\u0315\u0300\u1DF6\u0062'
        self.assertEqual(u'\u00E0\u0315\u1DF6\u035C\u0062', tf.normalize('NFC', text))

    def test_nfd_tus10(self):
        if self.version.minor < 7:
            return
        text = u'\u0061\u035C\u0315\u0300\u1DF6\u0062'
        self.assertEqual(u'\u0061\u0300\u0315\u1DF6\u035C\u0062', tf.normalize('NFD', text))

    def test_nfc_tus11(self):
        if self.version.minor < 7:
            return
        text = u'\u0061\u0315\u0300\u05AE\u09FE\u0062'
        self.assertEqual(u'\u00E0\u05AE\u09FE\u0315\u0062', tf.normalize('NFC', text))

    def test_nfd_tus11(self):
        if self.version.minor < 7:
            return
        text = u'\u0061\u0315\u0300\u05AE\u09FE\u0062'
        self.assertEqual(u'\u0061\u05AE\u0300\u09FE\u0315\u0062', tf.normalize('NFD', text))

    def test_nfc_tus12(self):
        if self.version.minor < 8:
            return
        text = u'\u0061\u0315\u0300\u05AE\U0001E136\u0062'
        self.assertEqual(u'\u00E0\u05AE\U0001E136\u0315\u0062', tf.normalize('NFC', text))

    def test_nfd_tus12(self):
        if self.version.minor < 8:
            return
        text = u'\u0061\u0315\u0300\u05AE\U0001E136\u0062'
        self.assertEqual(u'\u0061\u05AE\u0300\U0001E136\u0315\u0062', tf.normalize('NFD', text))

    def test_nfc_tus13(self):
        if self.version.minor < 9:
            return
        text = u'\u0061\u3099\u093C\U00016FF0\u09BC\u0062'
        self.assertEqual(u'\u0061\U00016FF0\u093C\u09BC\u3099\u0062', tf.normalize('NFC', text))

    def test_nfd_tus13(self):
        if self.version.minor < 9:
            return
        text = u'\u0061\u3099\u093C\U00016FF0\u09BC\u0062'
        self.assertEqual(u'\u0061\U00016FF0\u093C\u09BC\u3099\u0062', tf.normalize('NFD', text))

    def tests_nfc_tus14(self):
        if self.version.minor < 11:
            return
        text = u'\u0061\u0315\u0300\u05AE\u1ACC\u0062'
        self.assertEqual(u'\u00E0\u05AE\u1ACC\u0315\u0062', tf.normalize('NFC', text))

    def tests_nfd_tus14(self):
        if self.version.minor < 11:
            return
        text = u'\u0061\u0315\u0300\u05AE\u1ACC\u0062'
        self.assertEqual(u'\u0061\u05AE\u0300\u1ACC\u0315\u0062', tf.normalize('NFD', text))

    def tests_nfc_tus15(self):
        if self.version.minor < 12:
            return
        text = u'\u0061\u0315\u0300\u05AE\U0001E4EF\u0062'
        self.assertEqual(u'\u00E0\u05AE\U0001E4EF\u0315\u0062', tf.normalize('NFC', text))

    def tests_nfd_tus15(self):
        if self.version.minor < 12:
            return
        text = u'\u0061\u0315\u0300\u05AE\U0001E4EF\u0062'
        self.assertEqual(u'\u0061\u05AE\u0300\U0001E4EF\u0315\u0062', tf.normalize('NFD', text))

    # code still needs to be written for this
    def ignore_test_textMode(self):
        """Find occurrences of \r\r\n (that is CR CR LF) for a newline."""
        filename = 'text_mode.rawtxt'
        self.assertEqual(filename + ': confused', tf.process_file(None, None, None, filename))


if __name__ == '__main__':
    unittest.main()
