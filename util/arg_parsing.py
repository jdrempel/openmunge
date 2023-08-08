"""Argument parsing for the main openmunge script."""
import argparse
import pathlib

from util.config import setup_global_args, setup_global_config, write_config
from util.constants import Language, Platform, ALL_PLATFORMS, ALL_LANGUAGES, MUNGE_ALL


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


def parse_args():
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
    group.add_argument('-p', '--platform',
                       metavar='PLATFORM',
                       type=Platform,
                       choices=ALL_PLATFORMS,
                       default=Platform.PC,
                       help='The platform to target for munging files. Choices: %(choices)s. Default: %(default)s.')
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

    group = parser.add_argument_group('Global Options')
    group.add_argument('-P', '--project-dir',
                       type=pathlib.Path,
                       required=True,
                       help='The location of the project data to be munged. This should point to the data_ABC '
                            'directory (assuming ABC is the 3-letter code for the project).')
    group.add_argument('--config-file',
                       type=pathlib.Path,
                       default=pathlib.Path.home() / '.mungerc',
                       help='Location of a config file to use for global options. Command-line options take precedent '
                            'over option values read from this file. Default: %(default)s.')
    group.add_argument('-ll', '--log-level',
                       type=str,
                       choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'),
                       default='INFO',
                       help='The minimum level of log message to be displayed. '
                            'Choices: %(choices)s. Default: %(default)s.')
    group.add_argument('--swbf-path',
                       type=pathlib.Path,
                       default=None,
                       help='Location of the SWBF(1|2) installation where fully munged files will be copied. This '
                            'should point to the GameData directory.')

    group = parser.add_argument_group('Job Handling Options')
    group.add_argument('--max-concurrent-jobs',
                       metavar='NUM_JOBS',
                       type=PositiveNumberArgumentType(),
                       default=None,
                       help='The number of munge jobs that can be run simultaneously. If left unspecified, will '
                            'default to the number of CPUs available.')

    args = parser.parse_args()
    handle_and_verify_args(args)
    setup_global_args(args)
    setup_global_config()
    write_config(args.config_file)
    return args


def handle_and_verify_args(args: argparse.Namespace) -> None:
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
