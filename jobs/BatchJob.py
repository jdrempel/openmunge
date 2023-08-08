from abc import ABC
import pathlib

from jobs.JobBase import JobBase
from util.config import get_global_config


class BatchJob(JobBase, ABC):
    def get_executable_path(self):
        cwd = get_global_config('global.cwd')
        return pathlib.Path(cwd, 'run-batch').with_suffix('.py')

    def _get_name_prefix(self):
        batch_job = 'BatchJob'
        name_prefix = self.__class__.__name__.replace(batch_job, '')
        return name_prefix if name_prefix else batch_job

    def __str__(self):
        return self._get_name_prefix()

    def __repr__(self):
        return str(self)


class CommonBatchJob(BatchJob):
    @staticmethod
    def get_task():
        return 'common'


class LocalizeBatchJob(BatchJob):
    @staticmethod
    def get_task():
        return 'localize'


class SideBatchJob(BatchJob):
    @staticmethod
    def get_task():
        return 'side'

    def get_output_dir(self):
        return self.project_dir / '_BUILD' / 'Sides' / self.source_dir.stem / 'MUNGED' / self.platform.upper()

    def __str__(self):
        return 'Side:{}'.format(self.source_dir.stem)


class WorldBatchJob(BatchJob):
    @staticmethod
    def get_task():
        return 'world'

    def get_output_dir(self):
        return self.project_dir / '_BUILD' / 'Worlds' / self.source_dir.stem / 'MUNGED' / self.platform.upper()

    def __str__(self):
        return 'World:{}'.format(self.source_dir.stem)
