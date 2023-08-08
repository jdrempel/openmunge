import queue
import threading
import time
from datetime import datetime

from util.constants import StrEnum
from util.logs import setup_logger


class JobStatus(StrEnum):
    NOT_STARTED = 'not started'
    PENDING = 'pending'
    RUNNING = 'running'
    SUCCESS = 'success'
    ERROR = 'error'


COMPLETE_STATUSES = (JobStatus.SUCCESS, JobStatus.ERROR)


class JobRunner:
    RUNNER_SLEEP_TIME = 0.1
    RUNNER_WAIT_TIME = 0.1
    RUNNER_WAIT_REPORT_TIME = 30.0

    def __init__(self, max_concurrent=None):
        # Cap max concurrent at number of cpus
        from multiprocessing import cpu_count
        self.max_concurrent = max_concurrent or 999_999_999
        self.max_concurrent = min(self.max_concurrent, cpu_count())

        self.batches = queue.Queue()

        self.logger = setup_logger('JobRunner')
        self._thread = threading.Thread(target=self._run,)
        self._running = False

        self._current_batch: queue.Queue = queue.Queue()
        self._running_jobs: list = []
        self._has_work = False

    def add_batch(self, batch: list) -> None:
        self.batches.put(batch)

    def add_batches(self, batches: list) -> None:
        for batch in batches:
            self.batches.put(batch)

    def start(self):
        if self._running:
            self.logger.info('JobRunner is already running')
            return
        self.logger.info('Starting JobRunner...')
        self._running = True
        self._thread.start()

    def _run(self):
        # Main blocking loop
        while self._running:
            num_running = len(self._running_jobs)
            num_pending_in_batch = self._current_batch.qsize()
            num_batches_remaining = self.batches.qsize()
            self._has_work = num_running or num_pending_in_batch or num_batches_remaining

            if num_running:
                for i in range(num_running - 1, -1, -1):
                    job = self._running_jobs[i]
                    try:
                        job.update()
                        job_status = job.status()
                    except Exception as e:
                        self.logger.exception('Error while updating job status for {j_id}'.format(j_id=job.job_id()),
                                              exc_info=e)
                        job_status = JobStatus.ERROR

                    if job_status in COMPLETE_STATUSES:
                        self.logger.info('{j_id} status: {status}'.format(j_id=job.job_id(), status=job_status))

                        try:
                            job.complete(job_status)
                        except Exception as e:
                            self.logger.exception('Unable to complete job {j_id}'.format(j_id=job.job_id()), exc_info=e)

                        num_pending_in_batch = self._current_batch.qsize()
                        del self._running_jobs[i]

                        self.logger.info('{njobs} jobs pending in current batch, {nbatches} batches remaining'
                                         .format(njobs=num_pending_in_batch, nbatches=self.batches.qsize()))

            if num_pending_in_batch:
                num_to_submit = min(num_pending_in_batch, self.max_concurrent - num_running)
                for i in range(num_to_submit):
                    try:
                        job = self._current_batch.get()
                    except (IndexError, queue.Empty):
                        break

                    try:
                        job.prepare(self.logger)
                        job.execute()
                        self._running_jobs.append(job)
                    except Exception as e:
                        self.logger.exception('Unable to submit job {j_id}'.format(j_id=job.job_id()), exc_info=e)
                        job.complete(JobStatus.ERROR)

            if num_batches_remaining:
                next_batch = self.batches.get()
                for job in next_batch:
                    job.time_submit = time.time()
                    self._current_batch.put(job)

            time.sleep(JobRunner.RUNNER_SLEEP_TIME)

    def wait(self):
        time.sleep(2*JobRunner.RUNNER_SLEEP_TIME)  # To avoid an instantly-returning job locking things up
        t = datetime.now()
        while self._has_work:
            delta = datetime.now() - t
            if delta.seconds >= JobRunner.RUNNER_WAIT_REPORT_TIME:
                self.logger.info('{njobs} jobs are still running. '
                                 '{npending} jobs are pending in the current batch. '
                                 '{nbatches} batches are waiting.'
                                 .format(njobs=len(self._running_jobs), npending=self._current_batch.qsize(),
                                         nbatches=self.batches.qsize()))
                t = datetime.now()
            time.sleep(JobRunner.RUNNER_WAIT_TIME)

    def stop(self):
        if self._thread and self._running:
            self.logger.info('Stopping JobRunner...')
            self._running = False
            self._thread.join(timeout=10.0)
