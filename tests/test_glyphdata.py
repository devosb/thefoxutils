#!/usr/bin/python3

import unittest
import os
from pathlib import Path

from thefoxUtils import glyphdata

class UnikeyTests(unittest.TestCase):

    def setUp(self):
        os.chdir('tests/data/glyphdata')

    def tearDown(self):
        os.chdir('../../..')

    def test_rename(self):
        expected = Path('rename.csv').read_text().strip()
        ufo = glyphdata.read_ufo('../../font-psf-test/source/PsfTest-Regular.ufo')
        ref = glyphdata.read_csv('glyph_names.csv')
        rename = glyphdata.rename(None, ufo, ref)
        actual = '\n'.join(rename)
        assert actual == expected


if __name__ == '__main__':
    unittest.main()
