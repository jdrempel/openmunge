import pathlib
from abc import ABC

from jobs.JobBase import JobBase


class MungeJob(JobBase, ABC):
    def __init__(self, input_files: list, source_dir, project_dir, platform):
        super().__init__(source_dir, project_dir, platform)
        self.input_files = input_files

    def get_executable_path(self):
        return pathlib.Path(self.config.cwd, 'run-munger').with_suffix('.py')

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


class ConfigMungeJob(MungeJob):
    def __init__(self, input_files: list, source_dir, project_dir, platform, output_file=None, extension=None,
                 chunk_id=None):
        super().__init__(input_files, source_dir, project_dir, platform)
        self.output_file = output_file
        self.extension = extension
        self.chunk_id = chunk_id

    def build_cli_args(self) -> list:
        cli_args = super().build_cli_args()
        if self.output_file is not None:
            cli_args.extend(['--output-file', self.output_file])
        if self.extension is not None:
            cli_args.extend(['--extension', self.extension])
        if self.chunk_id is not None:
            cli_args.extend(['--chunk-id', self.chunk_id])
        return cli_args

    @staticmethod
    def get_task():
        return 'config'


class OdfMungeJob(MungeJob):
    @staticmethod
    def get_task():
        return 'odf'


class PlanningMungeJob(MungeJob):
    @staticmethod
    def get_task():
        return 'planning'


class WorldMungeJob(MungeJob):
    @staticmethod
    def get_task():
        return 'world'
