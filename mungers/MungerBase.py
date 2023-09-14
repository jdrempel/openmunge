import argparse
import pathlib
import sys
from abc import abstractmethod

from core.ScriptBase import ScriptBase
from core.config import Config
from util.string_util import str_in_i


class MungerBaseConfig(Config):
    def setup_options(self):
        self.add_option('source_dir',
                        alts=['-s'],
                        type=pathlib.Path,
                        help='The location in which all input files are contained.')
        self.add_option('output_dir',
                        alts=['-o'],
                        type=pathlib.Path,
                        help='The location where fully munged files will be placed.')


class MungerBase(ScriptBase):
    """
    Mungers correspond to individual munge operations like odfmunge or $PLATFORM_modelmunge.
    """
    def __init__(self, name):
        super().__init__(name)
        self.input_files = []

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
        group.add_argument('-H', '--hash-strings',
                           action='store_true',
                           help='When specified, hash strings as magic numbers in the munged files.')

    def create_base_config(self):
        base_config = MungerBaseConfig(self.name.lower())
        base_config.setup(self.arg_parser, args=self.job_args, only_known=True)
        return base_config

    def get_input_files(self):
        all_source_files = self.config.source_dir.glob('**/*')
        result = []
        for input_file_pattern in self.config.input_files:
            result.extend([file for file in all_source_files if str_in_i(file.suffix, input_file_pattern) and
                           file.is_file()])
        str_result = list(map(str, result))
        self.logger.debug('Input files:\n\t- {}'.format('\n\t- '.join(str_result)))
        return sorted(result)

    def start(self):
        self.print_setup_info()
        try:
            self.input_files = self.get_input_files()
            if not self.input_files:
                self.logger.info('No input files were found. Stopping...')
                return
            if not self.config.output_dir.exists():
                self.config.output_dir.mkdir(parents=True)
            self.run()
        except Exception as e:
            self.logger.exception('An error occurred while running {}.'.format(self.name), exc_info=e)
            sys.exit(1)
        self.logger.info('{} completed without errors.'.format(self.name))

    @abstractmethod
    def run(self):
        raise NotImplementedError
