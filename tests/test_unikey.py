#!/usr/bin/python3

from thefoxUtils import unikey


def test_modify():
    text = unikey.modify(r'BMP \u1D51 SMP \U0001D510')
    assert text == 'BMP \u1D51 SMP \U0001D510'

    text = unikey.modify(r'BMP \u1D51 SMP \u1D510')
    assert text == 'BMP \u1D51 SMP \U0001D510'


if __name__ == "__main__":
    test_modify()
