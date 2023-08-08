import pathlib
from abc import ABC

from jobs.JobBase import JobBase
from util.config import get_global_config


class MungeJob(JobBase, ABC):
    def __init__(self, input_files: list, source_dir, project_dir, platform):
        super().__init__(source_dir, project_dir, platform)
        self.input_files = input_files

    def get_executable_path(self):
        cwd = get_global_config('global.cwd')
        return pathlib.Path(cwd, 'run-munger').with_suffix('.py')

    def _get_name_prefix(self):
        job = 'Job'
        name_prefix = self.__class__.__name__.replace(job, '')
        return name_prefix if name_prefix else job

    def build_cli_args(self) -> list:
        cli_args = super().build_cli_args()
        cli_args.extend(['--input-files'] + self.input_files)
        return cli_args

    def __str__(self):
        return self._get_name_prefix()

    def __repr__(self):
        return str(self)


class OdfMungeJob(MungeJob):
    @staticmethod
    def get_task():
        return 'odf'


class WorldMungeJob(MungeJob):
    @staticmethod
    def get_task():
        return 'world'
