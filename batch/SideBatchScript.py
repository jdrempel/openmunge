from batch.BatchScriptBase import BatchScriptBase
from jobs.MungeJob import ConfigMungeJob, OdfMungeJob


class SideBatchScript(BatchScriptBase):
    def __init__(self):
        super().__init__('SideBatch')

    def run(self):
        base_args = (self.config.source_dir, self.config.project_dir, self.config.platform)

        batch = []

        batch.extend([
            OdfMungeJob(['$*.odf'], *base_args),
            ConfigMungeJob(['effects/*.fx'], *base_args),
            ConfigMungeJob(['$*.combo'], *base_args),
            # ModelMungeJob(['$*.msh'], *base_args),
            # TextureMungeJob(['$*.tga', '$*.pic'], *base_args),
            ConfigMungeJob(['*.snd', '*.mus'], *base_args, hash_strings=True)
        ])

        self.job_runner.add_batch(batch)
        self.job_runner.start()
        self.job_runner.wait()
        self.logger.info('Side {} done!'.format(self.config.source_dir.stem))
