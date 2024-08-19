#!/usr/bin/python3

import argparse
from collections import Counter

import fontParts.world as fontparts

from thefoxUtils import version


def main():
    parser = argparse.ArgumentParser(description='Review and cleanup composites')
    parser.add_argument('-c', '--cleanup', help='Cleanup composites', action='store_true')
    parser.add_argument('ufo', help='UFO')
    parser.add_argument('--version', action='version', version='%(prog)s ' + version)

    args = parser.parse_args()

    font = fontparts.OpenFont(args.ufo)
    possible_cleanup = dict()
    cleanup = dict()
    shared_components = Counter()
    for glyph in font:
        if len(glyph.components) > 0:
            for component in glyph.components:
                flag = False
                component_glyph = font[component.baseGlyph]
                if component_glyph.unicode:
                    pass
                elif '_' in component.baseGlyph:
                    # handles both ligatures (glyph1_glyph2) and parts (_glyph)
                    pass
                elif '.' in component_glyph.name:
                    component_base_glyph_name = component.baseGlyph.split('.')[0]
                    if component_base_glyph_name not in font:
                        flag = True
                else:
                    flag = True
                if flag:
                    shared_components[component.baseGlyph] += 1
                    possible_cleanup[glyph.name] = component.baseGlyph

    for glyph_name, base_glyph_name in possible_cleanup.items():
        names = f'{base_glyph_name} from {glyph_name}'
        if shared_components[base_glyph_name] > 1:
            print(f'Note: {names} is shared by {shared_components[base_glyph_name]} other glyphs')
        else:
            print(f'Fix: {names} can be cleaned up')
            cleanup[glyph_name] = base_glyph_name

    if args.cleanup:
        for glyph_name, base_glyph_name in cleanup.items():
            print(f'Info: {base_glyph_name} from {glyph_name} is being cleaned up')
            glyph = font[glyph_name]
            glyph.decompose()
            del font[base_glyph_name]

        font.changed()
        font.save()
        font.close()


if __name__ == '__main__':
    main()
