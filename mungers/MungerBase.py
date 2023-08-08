import argparse
import pathlib
import sys
from abc import abstractmethod

from core.ScriptBase import ScriptBase
from util.constants import Platform, ALL_PLATFORMS
from util.string_util import pretty_print_args


class MungerBase(ScriptBase):
    """
    Mungers correspond to individual munge operations like odfmunge or $PLATFORM_modelmunge.
    """
    def create_base_args(self):
        original_prog = pathlib.Path(sys.argv[0]).name
        short_name = self.name.replace('Munge', '').lower()
        self.arg_parser = argparse.ArgumentParser(prog='{orig} {name}'.format(orig=original_prog, name=short_name))

        group = self.arg_parser.add_argument_group('Base Munge Options')
        group.add_argument('-i', '--input-files',
                           type=str,
                           nargs='+',
                           required=True,
                           help='A set of files in SOURCE_DIR to be used as munge inputs. Can use a wildcard * pattern '
                                'but ensure args using the wildcard are wrapped in quotes. Prefix any arg with $ to '
                                'perform recursive search for matching files in the subdirectories of SOURCE_DIR.')
        group.add_argument('-s', '--source-dir',
                           type=pathlib.Path,
                           required=True,
                           help='The location in which all input files are contained.')
        group.add_argument('-o', '--output-dir',
                           type=pathlib.Path,
                           required=True,
                           help='The location where fully munged files will be placed.')
        group.add_argument('-p', '--platform',
                           type=Platform,
                           required=True,
                           choices=ALL_PLATFORMS,
                           help='The platform to target for munging files. Choices: %(choices)s. Default: %(default)s.')
        group.add_argument('-H', '--hash-strings',
                           action='store_true',
                           help='When specified, hash strings as magic numbers in the munged files.')

    def start(self):
        self.logger.info('Starting {}...'.format(self.name))
        self.logger.info('{name} Config:\n\tArgs: {args}'.format(name=self.name, args=' '.join(sys.argv)))
        try:
            self.run()
        except Exception as e:
            self.logger.exception('An error occurred while running {}.'.format(self.name), exc_info=e)
            sys.exit(1)
        self.logger.info('{} completed without errors.'.format(self.name))

    @abstractmethod
    def run(self):
        raise NotImplementedError
