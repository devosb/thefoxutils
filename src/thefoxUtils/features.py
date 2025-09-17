#!/usr/bin/python3

import argparse
from fontTools.feaLib.parser import Parser
# from fontTools.ttLib import TTFont
import fontTools.feaLib.ast as ast
from pathlib import Path
# from ufoLib2.objects import Font

from thefoxUtils import version


def main():
    parser = argparse.ArgumentParser(description='User features')
    parser.add_argument('ufo', help='UFO', type=Path)
    parser.add_argument('--version', action='version', version='%(prog)s ' + version)
    args = parser.parse_args()

    user_features(args.ufo)


def user_features(ufo):
    """Read user features from a feature file"""
    parser = Parser(ufo / 'features.fea')
    doc = parser.parse()
    for statement in doc.statements:
        if type(statement) is ast.FeatureBlock:
            if statement.name.startswith('cv'):
                print(statement.name)
                for nested_statement in statement.statements:
                    if type(nested_statement) is ast.NestedBlock:
                        for cv_statement in nested_statement.statements:
                            if type(cv_statement) is ast.NestedBlock:
                                print(f'{cv_statement.tag} {cv_statement.block_name}')
                                for name_statement in cv_statement.statements:
                                    if type(name_statement) is ast.CVParametersNameStatement:
                                        print(f'{name_statement.nameID} {name_statement.block_name} {name_statement.string}')


if __name__ == '__main__':
    main()
