import hashlib
import os
import pathlib
import shutil
import subprocess
import time
from abc import abstractmethod, ABC

from jobs.JobRunner import JobStatus, COMPLETE_STATUSES
from core.config import get_global_config
from util.constants import Platform


class JobBase(ABC):
    def __init__(self, source_dir: pathlib.Path, project_dir: pathlib.Path, platform: Platform):
        self.id = None
        self.result_manager = None
        self.runner_log = None

        self.log_file_path = None
        self.log_file = None
        self.process = None

        self.time_submit = None
        self.time_start = None
        self.time_finish = None

        self.source_dir = source_dir
        self.project_dir = project_dir
        self.platform = platform

        self.config = get_global_config()

    def job_id(self):
        munge_type = self._get_name_prefix()
        source_stem = self.source_dir.stem
        run_signature = self.run_signature()
        if munge_type == source_stem:
            return '{typ}_{sig}'.format(typ=munge_type, sig=run_signature)
        return '{typ}-{stem}_{sig}'.format(typ=munge_type, sig=run_signature, stem=source_stem)

    def run_signature(self):
        hasher = hashlib.md5()
        hasher.update('name={}'.format(str(self.get_task())).encode('ascii'))
        hasher.update('source={}'.format(str(self.source_dir)).encode('ascii'))
        if hasattr(self, 'input_files'):
            hasher.update('inputs={}'.format(str(self.input_files)).encode('ascii'))

        return hasher.hexdigest()[:8]

    @abstractmethod
    def get_executable_path(self):
        ...

    @staticmethod
    @abstractmethod
    def get_task():
        ...

    def get_output_dir(self):
        return self.project_dir / '_BUILD' / self.source_dir.stem / 'MUNGED' / self.platform.upper()

    @abstractmethod
    def _get_name_prefix(self):
        ...

    def build_cli_args(self) -> list:
        which_python = shutil.which('python')
        if which_python is None:
            which_python3 = shutil.which('python3')
            if which_python3 is None:
                cmd = []
            else:
                cmd = ['python3']
        else:
            cmd = ['python']

        if not cmd:
            raise EnvironmentError('Unable to find a command or executable named "python" or "python3" in the '
                                   'current environment')

        app_path = self.get_executable_path()
        if not app_path.exists() or not app_path.is_file():
            raise OSError('{job}: {path} does not exist or is not executable.'.format(job=self.job_id(), path=app_path))
        cmd.append(str(app_path))
        cmd.append(self.get_task())

        cmd.extend(['--source-dir', str(self.source_dir)])
        cmd.extend(['--output-dir', str(self.get_output_dir())])

        return cmd

    def prepare(self, job_runner_log):
        if self.id is None:
            self.id = self.run_signature()

        self.runner_log = job_runner_log

        # Set up log file for this job
        self.log_file_path = self.config.cwd / '{j_id}.log'.format(j_id=self.job_id())
        self.log_file = open(self.log_file_path, 'w')

    def execute(self):
        self.time_start = time.time()
        # popen stuff...
        job_args = self.build_cli_args()
        sub_env = os.environ | self.config.get_options_as_env_dict('project_dir', 'platform', 'config_file',
                                                                   'log_level')
        self.runner_log.info('{j_id} args: {args}'.format(j_id=self.job_id(), args=' '.join(job_args)))
        self.process = subprocess.Popen(job_args, stdout=self.log_file, stderr=self.log_file, env=sub_env)

    def update(self):
        ...

    def status(self) -> str:
        if not self.process:
            return JobStatus.NOT_STARTED
        process_running = self.process and self.process.poll() is None
        if process_running:
            if not self.time_start:
                return JobStatus.PENDING
            return JobStatus.RUNNING
        exit_status = self.process.returncode
        if exit_status != 0:
            return JobStatus.ERROR
        return JobStatus.SUCCESS

    def complete(self, status):
        if self.time_finish is None:
            self.time_finish = time.time()

        if status in COMPLETE_STATUSES and self.result_manager is not None:
            self.result_manager(self, status)

        if self.log_file:
            self.log_file.close()
            self.log_file = None
