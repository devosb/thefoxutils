# thefoxutils
Unicode utilities

## unidump

To create the Unicode Character Database (UCD) cache that unidump uses, run

- `mkdir ~/.unidump`
- `unidump --ucd UnicodeData.txt tests/data/unidump/branch.txt tests/data/unidump/microsoft.txt tests/data/unidump/sil.txt`

where the file `UnicodeData.txt` comes from https://www.unicode.org/Public/UCD/latest/ucd/UnicodeData.txt

## release

- `bumpversion minor`
- `git push --follow-tags`

## testing release

- python3 -m venv venv
- source venv/bin/activate
- pip3 install fontParts
- pip3 install uharfbuzz
- pip3 install cssutils
- pip install -i https://test.pypi.org/simple/ thefoxUtils
