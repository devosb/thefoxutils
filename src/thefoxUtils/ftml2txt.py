#!/usr/bin/python3

import argparse
import os
import os.path
from xml.etree.ElementTree import ElementTree

from thefoxUtils import version, unikey


def main():
    parser = argparse.ArgumentParser(description='Extract text from FTML files')
    parser.add_argument('-o', '--output', help='Output directory')
    parser.add_argument('-s', '--sample', help='Sample project to reference')
    parser.add_argument('file', help='FTML files to process', nargs='+')
    parser.add_argument('--version', action='version', version='%(prog)s ' + version)
    args = parser.parse_args()

    if args.sample:
        project_filenames = sorted(os.listdir(args.sample))
        book_filenames = [project_filename for project_filename in project_filenames if project_filename.endswith('SFM')]

    dev = ''
    if args.output:
        dev = args.output
    for ftml_filename in args.file:
        # Parse FTML data
        ftml_data = FTML()
        ftml_data.parse(ftml_filename)

        # Construct output filename
        (base_filename, ext) = os.path.splitext(ftml_filename)

        # Write plain text file
        text_filename = f'{dev}/txt/{base_filename}.txt'
        with open(text_filename, 'w', encoding='utf-8') as text_file:
            text = ftml_data.text()
            text_file.write(text)

        # Write HTML file
        html_filename = f'{dev}/web/{base_filename}.html'
        with open(html_filename, 'w', encoding='utf-8') as html_file:
            html = ftml_data.html()
            html_file.write(html)

        if not args.sample:
            continue

        # Write SFM file
        book_filename = book_filenames.pop(0)
        sfm_filename = f'{dev}/sfm/{book_filename}'
        with open(sfm_filename, 'w', encoding='utf-8', newline='\r\n') as sfm_file:
            sfm = ftml_data.sfm(base_filename, book_filename)
            sfm_file.write(sfm)


class FTML:
    """Test data in an FTML file"""

    def __init__(self):
        self.testgroups = list()
        self.testgroup = None

    def parse(self, ftml_filename):
        """Parse FTML file"""

        # Read FTML file
        ftml = ElementTree()
        ftml.parse(ftml_filename)

        # Extract text from FTML file
        for testgroup in ftml.iter('testgroup'):
            tests = self.add_testgroup(testgroup.get('label'))
            for test in testgroup.iter('test'):
                label = test.get('label')
                comment = test.findtext('comment', '')
                raw_data = test.find('string').text
                char_data = unikey.modify(raw_data)
                data = ''
                for char in char_data:
                    codepoint = ord(char)
                    if codepoint < 0x20 or 0x2028 <= codepoint <= 0x2029:
                        pass
                    else:
                        data += char
                tests.add_test(label, comment, data)

    def add_testgroup(self, data):
        """Add a TestGroup with data"""
        testgroup = TestGroup(data)
        self.testgroups.append(testgroup)
        return testgroup

    def text(self):
        """Format data for a plain text file"""
        text = ''
        for testgroup in self.testgroups:
            text += testgroup.text()
        return text

    def html(self):
        """Format data for a HTML file"""
        html = """<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="dev.css" type="text/css">
<meta charset="utf-8">
</head>
<body>
"""
        for testgroup in self.testgroups:
            html += testgroup.html()
        html += """</body>
</html>
"""
        return html

    def sfm(self, ftml_name, book_filename):
        book_code = book_filename[2:5]
        """Format data for a SFM file"""
        sfm = fr"""\id {book_code}
\ide UTF-8
\rem {ftml_name}
\h {book_code}
\mt {ftml_name}
\c 1
\cp ?
\s section
\p
\v 1 \vp ???\vp* ?????????????????
"""
        sfm = fr"""\id {book_code}
\mt {ftml_name}
"""
        chapter = 0
        for testgroup in self.testgroups:
            chapter += 1
            sfm += f'\\c {chapter}\n'
            sfm += testgroup.sfm()
        return sfm


class TestGroup:
    """Test group in an FTML file"""

    def __init__(self, label):
        self.data = label
        self.tests = list()

    def add_test(self, label, comment, data):
        """Add test"""
        test = Test(label, comment, data)
        self.tests.append(test)
        return test

    def text(self):
        """Format data for a plain text file"""
        text = '# ' + self.data + '\n'
        for test in self.tests:
            text += test.text()
        for char in r'\#$&_':  # \#$%&()^_~
            text = text.replace(char, '\\' + char)
        return text

    def html(self):
        """Format data for a HTML file"""
        html = '<h1>' + self.data + '</h1>\n'
        for test in self.tests:
            html += test.html()
        return html

    def sfm(self):
        """Format data for a SFM file"""
        sfm = '\\s ' + self.data + '\n\\p\n'
        verse = 0
        for test in self.tests:
            verse += 1
            sfm += f'\\v {verse} '
            sfm += test.sfm()
        return sfm


class Test:
    """Test in an FTML file"""

    def __init__(self, label, comment, data):
        self.label = label
        self.comment = comment
        self.data = data

    def text(self):
        """Format data for a plain text file"""
        return self.label + ': ' + self.comment + ' ' + self.data + '\n'

    def html(self):
        """Format data for a HTML file"""
        label = f'<p>{self.label}: {self.comment}</p>\n'
        local = f'<p>{self.data}</p>\n'
        woff2 = f'<p class=dev>{self.data}</p>\n'
        return label + local + woff2

    def sfm(self):
        """Format data for a SFM file"""
        sfm = self.label + ': ' + self.comment + ' ' + self.data + '\n'
        sfm = sfm.replace('\u005C', '')
        return sfm


if __name__ == "__main__":
    main()
