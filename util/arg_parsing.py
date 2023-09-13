"""Argument parsing for the main openmunge script."""
import argparse

from util.constants import Language, ALL_LANGUAGES, MUNGE_ALL


class PositiveNumberArgumentType:
    def __init__(self):
        pass

    def __call__(self, x):
        try:
            x = int(x)
        except ValueError:
            raise argparse.ArgumentTypeError('Must be an integer')
        if x <= 0:
            raise argparse.ArgumentTypeError('Must be a positive integer')
        return x


def get_base_parser():
    parser = argparse.ArgumentParser(prog='openmunge')

    group = parser.add_argument_group('Munge Options')
    group.add_argument('-w', '--worlds',
                       nargs='*',
                       default=[],
                       help='One or more Worlds to munge, or EVERYTHING. E.g. -w ABC -w XYZ')
    group.add_argument('-s', '--sides',
                       nargs='*',
                       default=[],
                       help='One or more Sides to munge, or EVERYTHING. E.g. -s ALL -s IMP')
    group.add_argument('-c', '--common',
                       action='store_true',
                       help='When specified, munge Common assets.')
    group.add_argument('-l', '--load',
                       action='store_true',
                       help='When specified, munge Load screen assets.')
    group.add_argument('-e', '--shell',
                       action='store_true',
                       help='When specified, munge Shell interface assets.')
    group.add_argument('-m', '--movies',
                       action='store_true',
                       help='When specified, munge Movie assets.')
    group.add_argument('-z', '--localize',
                       action='store_true',
                       help='When specified, munge Localization configs.')
    group.add_argument('-S', '--sound',
                       action='store_true',
                       help='When specified, munge Sounds.')
    group.add_argument('-L', '--language',
                       metavar='LANGUAGE',
                       type=Language,
                       choices=ALL_LANGUAGES,
                       default=Language.ENGLISH,
                       help='The language to target when munging. Choices: %(choices)s. Default: %(default)s.')
    group.add_argument('-a', '--all',
                       action='store_true',
                       dest='munge_all',
                       help='When specified, munge every World and Side, as well as Common, Load, Shell, Movies, '
                            'Localization, and Sounds. Setting this option will override any values provided to '
                            'the above-mentioned munge options.')

    return parser


def handle_and_verify_base_args(args: argparse.Namespace) -> None:
    if args.munge_all:
        args.worlds = [MUNGE_ALL]
        args.sides = [MUNGE_ALL]
        args.common = args.load = args.shell = args.movies = args.localize = args.sound = True

    if MUNGE_ALL in args.worlds and len(args.worlds) > 1:
        args.worlds = [MUNGE_ALL]
    if MUNGE_ALL in args.sides and len(args.sides) > 1:
        args.sides = [MUNGE_ALL]

    args.worlds = [x.upper() for x in args.worlds if x != 'Common']  # Always do common anyway
    args.sides = [x.upper() for x in args.sides]
