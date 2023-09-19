import pathlib
import re
from abc import ABC

from jobs.JobBase import JobBase

JOB_ID_REMOVE_INPUT_FILE_CHARS_RE = re.compile(r'[^\dA-Za-z_-]')


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
    def __init__(self, input_files: list, source_dir, project_dir, platform, hash_strings=False, output_file=None,
                 extension=None, chunk_id=None):
        super().__init__(input_files, source_dir, project_dir, platform)
        self.hash_strings = hash_strings
        self.output_file = output_file
        self.extension = extension
        self.chunk_id = chunk_id

    def job_id(self):
        base_job_id = super().job_id()
        clean_input_files = [re.sub(JOB_ID_REMOVE_INPUT_FILE_CHARS_RE, '_', str(f)) for f in self.input_files]
        input_files_str = '_'.join(clean_input_files)
        input_files_deduped = re.sub(r'(_)\1+', '\\1', input_files_str)  # De-duplicate underscores
        input_files_stripped = input_files_deduped.strip('_')
        if self.output_file is not None:
            input_files_stripped += f'_{self.output_file}'
        return f'{base_job_id}_{input_files_stripped}'

    def build_cli_args(self) -> list:
        cli_args = super().build_cli_args()
        if self.hash_strings:
            cli_args.extend(['--hash-strings'])
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

    def job_id(self):
        base_job_id = super().job_id()
        clean_input_files = [re.sub(JOB_ID_REMOVE_INPUT_FILE_CHARS_RE, '_', str(f)) for f in self.input_files]
        input_files_str = '_'.join(clean_input_files)
        input_files_deduped = re.sub(r'(_)\1+', '\\1', input_files_str)  # De-duplicate underscores
        input_files_stripped = input_files_deduped.strip('_')
        return f'{base_job_id}_{input_files_stripped}'
