from batch.BatchScriptBase import BatchScriptBase
from jobs.MungeJob import ConfigMungeJob, OdfMungeJob


class CommonBatchScript(BatchScriptBase):
    def __init__(self):
        super().__init__('CommonBatch')

    def run(self):
        base_args = (self.config.source_dir, self.config.project_dir, self.config.platform)

        batch = []

        batch.extend([
            OdfMungeJob(['$*.odf'], *base_args),
            ConfigMungeJob(['*.fx'], *base_args),
            ConfigMungeJob(['$*.combo'], *base_args),
            # ScriptMunge(['$*.lua'], *base_args),
            ConfigMungeJob(['$*.mcfg'], *base_args, hash_strings=True),
            ConfigMungeJob(['$*.sanm'], *base_args),
            ConfigMungeJob(['$*.hud'], *base_args),
            # FontMungeJob(['$*.fff'], *base_args),
            # TextureMungeJob(['$*.tga', '$*.pic'], *base_args),
            # ModelMungeJob(['$Effects/*.msh', '$MSHs/*.msh'], *base_args),
            # ShaderMunge(['shaders/*.xml', 'shaders/*.vsfrag'], *base_args),  # TODO what does -I do again?
            ConfigMungeJob(['*.snd', '*.mus'], *base_args, hash_strings=True),
            # SoundFlMungeJob(['*.sfx']),
            # SoundFlMungeJob(['*.stm']),
        ])

        # Munge sprites
        # Merge localization

        # batch.append(LocalizeMunge(['*.cfg'], *base_args))

        self.job_runner.add_batch(batch)
        self.job_runner.start()
        self.job_runner.wait()
        self.logger.info('Common done!'.format(self.config.source_dir.stem))
