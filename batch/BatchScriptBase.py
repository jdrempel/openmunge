import pathlib
import sys
from abc import abstractmethod

from core.ScriptBase import ScriptBase
from jobs.JobRunner import JobRunner
from core.config import Config


class BatchScriptBaseConfig(Config):
    def setup_options(self):
        self.add_option('source_dir',
                        alts=['-s'],
                        type=pathlib.Path,
                        help='The location in which all input files are contained.')


class BatchScriptBase(ScriptBase):
    """
    Tasks correspond to 'big-picture' jobs like munging Common or munging a single Side. They are 1:1 with MungeJobs,
    generally speaking.
    """
    def __init__(self, name: str):
        super().__init__(name)
        self.job_runner = None

    def create_base_args(self):
        pass

    def create_base_config(self):
        base_config = BatchScriptBaseConfig(self.name.lower())
        base_config.setup(self.arg_parser, args=self.job_args, only_known=True)
        return base_config

    def start(self):
        self.job_runner = JobRunner()
        self.print_setup_info()
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
