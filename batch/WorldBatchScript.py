from batch.BatchScriptBase import BatchScriptBase
from jobs.MungeJob import WorldMungeJob, PathMungeJob


class WorldBatchScript(BatchScriptBase):
    def __init__(self):
        super().__init__('WorldBatch')

    def run(self):
        base_args = (self.args.source_dir, self.args.project_dir, self.args.platform)
        batch = [
            PathMungeJob(['$*.pth'], *base_args),
            WorldMungeJob(['$*.lyr'], *base_args),
            WorldMungeJob(['$*.wld'], *base_args),
        ]
        self.job_runner.add_batch(batch)
        self.job_runner.start()
        self.job_runner.wait()
        self.logger.info('World done!')
