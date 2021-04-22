#!/usr/bin/python3

import unittest
from thefoxUtils import tf


class TextFileTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # Line endings

    def test_dos(self):
        filename = 'data/dos.rawtxt'
        self.assertEqual('nl: dos ws: eol', tf.process_file(None, None, None, filename))

    def test_mac(self):
        filename = 'data/mac.rawtxt'
        self.assertEqual('nl: mac', tf.process_file(None, None, None, filename))

    def test_unix(self):
        filename = 'data/unix.rawtxt'
        self.assertEqual('ws: eol eof', tf.process_file(None, None, None, filename))

    def test_missing_dos(self):
        filename = 'data/missing-dos.rawtxt'
        self.assertEqual('nl: dos missing ws: eol', tf.process_file(None, None, None, filename))

    def test_missing_unix(self):
        filename = 'data/missing-unix.rawtxt'
        self.assertEqual('nl: unix missing ws: eol', tf.process_file(None, None, None, filename))

    def test_changeOS(self):
        filename = 'data/change_os.rawtxt'
        self.assertEqual('nl: dos unix ws: eof', tf.process_file(None, None, None, filename))

    # Normalization forms

    def test_nf_c(self):
        filename = 'data/nf-c.txt'
        self.assertEqual('nf: c', tf.process_file(None, None, None, filename))

    def test_nf_d(self):
        filename = 'data/nf-d.txt'
        self.assertEqual('nf: d', tf.process_file(None, None, None, filename))

    def test_nf_both(self):
        filename = 'data/nf-both.txt'
        self.assertEqual('', tf.process_file(None, None, None, filename))

    def test_nf_none(self):
        filename = 'data/nf-none.txt'
        self.assertEqual('nf:', tf.process_file(None, None, None, filename))

    def test_nfc_tus1(self):
        text = u'e\u0301'
        self.assertEqual(u'\u00e9', tf.normalize('NFC', text))

    def test_nfd_tus1(self):
        text = u'\u00e9'
        self.assertEqual(u'e\u0301', tf.normalize('NFD', text))

    def ignore_nfc_tus10(self):
        text = u'\u0061\u035C\u0315\u0300\u1DF6\u0062'
        self.assertEqual(u'\u00E0\u0315\u1DF6\u035C\u0062', tf.normalize('NFC', text))

    def ignore_nfd_tus10(self):
        text = u'\u0061\u035C\u0315\u0300\u1DF6\u0062'
        self.assertEqual(u'\u0061\u0300\u0315\u1DF6\u035C\u0062', tf.normalize('NFD', text))

    def ignore_nfc_tus11(self):
        text = u'\u0061\u0315\u0300\u05AE\u09FE\u0062'
        self.assertEqual(u'\u00E0\u05AE\u09FE\u0315\u0062', tf.normalize('NFC', text))

    def ignore_nfd_tus11(self):
        text = u'\u0061\u0315\u0300\u05AE\u09FE\u0062'
        self.assertEqual(u'\u0061\u05AE\u0300\u09FE\u0315\u0062', tf.normalize('NFD', text))

    def ignore_nfc_tus12(self):
        text = u'\u0061\u0315\u0300\u05AE\U0001E136\u0062'
        self.assertEqual(u'\u00E0\u05AE\U0001E136\u0315\u0062', tf.normalize('NFC', text))

    def ignore_nfd_tus12(self):
        text = u'\u0061\u0315\u0300\u05AE\U0001E136\u0062'
        self.assertEqual(u'\u0061\u05AE\u0300\U0001E136\u0315\u0062', tf.normalize('NFD', text))

    def ignore_nfc_tus13(self):
        text = u'\u0061\u3099\u093C\U00016FF0\u09BC\u0062'
        self.assertEqual(u'\u0061\U00016FF0\u093C\u09BC\u3099\u0062', tf.normalize('NFC', text))

    def ignore_nfd_tus13(self):
        text = u'\u0061\u3099\u093C\U00016FF0\u09BC\u0062'
        self.assertEqual(u'\u0061\U00016FF0\u093C\u09BC\u3099\u0062', tf.normalize('NFD', text))

    # code still needs to be written for this
    def ignore_test_textMode(self):
        """Find occurrences of \r\r\n (that is CR CR LF) for a newline."""
        filename = 'data/text_mode.rawtxt'
        self.assertEqual(filename + ': confused', tf.process_file(None, None, None, filename))


if __name__ == '__main__':
    unittest.main()
