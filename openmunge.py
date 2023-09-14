from jobs.JobRunner import JobRunner
from jobs.batching import get_work_batches
from util.arg_parsing import get_base_parser, handle_and_verify_base_config
from core.config import setup_global_config
from util.logs import setup_logger


def main():
    arg_parser = get_base_parser()
    config = setup_global_config(arg_parser)
    handle_and_verify_base_config(config)
    log = setup_logger('openmunge')

    # Set up work batches
    # Inputs: global args
    # Effects: from global args we form paths to the relevant munge-able data, and determine order of operations
    # Outputs: work batches, each batch containing some number of jobs to be executed simultaneously, each batch after
    #          the other
    work_batches = get_work_batches()
    log.info('Created {n} work batches'.format(n=len(work_batches)))

    # Set up and configure job runner
    # Inputs: args
    # Effects: settings like max number of concurrent jobs are recorded into a job runner instance
    # Outputs: a fully configured job runner instance
    job_runner = JobRunner(max_concurrent=config.max_concurrent_jobs)
    job_runner.add_batches(work_batches)

    # Run jobs
    # Inputs: work batches and job runner
    # Effects: each work batch is executed in sequence, munged files are output to their respective destinations
    # Outputs: summary of job statuses and paths to munged outputs
    try:
        job_runner.start()
        job_runner.wait()
    finally:
        job_runner.stop()

    # Process results
    # Inputs: job status summary, paths to munged outputs
    # Effects: failed jobs are reported and cause failure if present, expected output files are confirmed to exist
    # Outputs: none

    # Copy results
    # Inputs: paths to munged outputs
    # Effects: outputs files are copied to their destinations
    # Outputs: none

    # Done?


if __name__ == '__main__':
    main()
