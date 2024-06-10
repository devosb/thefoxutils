#!/usr/bin/python3

import os
import tempfile
import unittest

from thefoxUtils import unikey


class UnikeyTests(unittest.TestCase):

    def setUp(self):
        os.chdir('tests/data/unikey')
        self.output_file, self.output_filename = tempfile.mkstemp()
        self.standard = r'BMP \u1D51 SMP \U0001D510'
        self.extension = r'BMP \u1D51 SMP \u1D510'
        self.result = 'BMP \u1D51 SMP \U0001D510'

    def tearDown(self):
        os.chdir('../../..')
        os.remove(self.output_filename)

    def test_modify_standard(self):
        text = unikey.modify(self.standard)
        assert text == self.result

    def test_modify_extension(self):
        text = unikey.modify(self.extension)
        assert text == self.result

    def test_file_standard(self):
        unikey.create(self.output_filename, ['standard.htxt'])
        with open(self.output_filename, 'r', encoding='utf-8') as output_file:
            text = output_file.read()
            assert text == self.result + '\n'

    def test_file_extension(self):
        unikey.create(self.output_filename, ['extension.htxt'])
        with open(self.output_filename, 'r', encoding='utf-8') as output_file:
            text = output_file.read()
            assert text == self.result + '\n'


if __name__ == "__main__":
    unittest.main()
