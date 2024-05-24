#!/usr/bin/python3

import fontParts.world as fontparts
import argparse


def main():
    parser = argparse.ArgumentParser(description='Review and cleanup composites')
    parser.add_argument('-c', '--cleanup', help='Cleanup composites', action='store_true')
    parser.add_argument('ufo', help='UFO')
    args = parser.parse_args()

    font = fontparts.OpenFont(args.ufo)
    cleanup = dict()
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
                    print(f'Warning: {component.baseGlyph} from {glyph.name} can be cleaned up')
                    cleanup[glyph.name] = component.baseGlyph

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
