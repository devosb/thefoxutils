#!/usr/bin/python3

import fontParts.world as fontparts
import argparse


def main():
    parser = argparse.ArgumentParser(description='Review and fix composites')
    parser.add_argument('ufo', help='UFO')
    args = parser.parse_args()

    font = fontparts.OpenFont(args.ufo)
    for glyph in font:
        flag = False
        if len(glyph.components) > 0:
            for component in glyph.components:
                component_glyph = font[component.baseGlyph]
                if component_glyph.unicode:
                    pass
                elif '.' in component_glyph.name:
                    component_base_glyph_name = component.baseGlyph.split('.')[0]
                    if component_base_glyph_name not in font:
                        flag = True
                elif '_' in component.baseGlyph:
                    # handles both ligatures (glyph1_glyph2) and parts (_glyph)
                    pass
                else:
                    flag = True
                if flag:
                    print(f'{glyph.name}: {component.baseGlyph}')
                    # glyph.decompose()
                    # font.removeGlyph(component.baseGlyph)
                    # del font[component.baseGlyph]
        if flag:
            pass


if __name__ == '__main__':
    main()
