import argparse
import pathlib
import sys
from abc import abstractmethod

from core.ScriptBase import ScriptBase
from jobs.JobRunner import JobRunner
from util.constants import Platform, ALL_PLATFORMS


class BatchScriptBase(ScriptBase):
    """
    Tasks correspond to 'big-picture' jobs like munging Common or munging a single Side. They are 1:1 with MungeJobs,
    generally speaking.
    """
    def __init__(self, name: str):
        super().__init__(name)
        self.job_runner = None

    def create_base_args(self):
        self.arg_parser = argparse.ArgumentParser()

        group = self.arg_parser.add_argument_group('Base Task Options')
        group.add_argument('-s', '--source-dir',
                           type=pathlib.Path,
                           required=True,
                           help='The location in which all input files are contained.')
        group.add_argument('-p', '--platform',
                           type=Platform,
                           required=True,
                           choices=ALL_PLATFORMS,
                           help='The platform to target for munging files. Choices: %(choices)s. Default: %(default)s.')

        group = self.arg_parser.add_argument_group('Global Options')
        group.add_argument('-P', '--project-dir',
                           type=pathlib.Path,
                           required=True,
                           help='The location of the project data to be munged. This should point to the data_ABC '
                                'directory (assuming ABC is the 3-letter code for the project).')
        group.add_argument('-ll', '--log-level',
                           type=str,
                           choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'),
                           default='INFO',
                           help='The minimum level of log message to be displayed. '
                                'Choices: %(choices)s. Default: %(default)s.')

    def start(self):
        self.job_runner = JobRunner()
        self.logger.info('Starting {}...'.format(self.name))
        self.logger.info('{name} Setup:\n\tConfig File: {config}\n\tArgs: {args}'
                         .format(name=self.name, config=None, args=' '.join(sys.argv)))
        try:
            self.run()
        except Exception as e:
            self.logger.exception('An error occurred while running {}.'.format(self.name), exc_info=e)
            sys.exit(1)
        finally:
            self.job_runner.stop()
        self.logger.info('{} completed without errors.'.format(self.name))

    @abstractmethod
    def run(self):
        raise NotImplementedError
