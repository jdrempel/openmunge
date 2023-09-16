from batch.BatchScriptBase import BatchScriptBase
from jobs.MungeJob import WorldMungeJob, ConfigMungeJob, OdfMungeJob, PlanningMungeJob


class WorldBatchScript(BatchScriptBase):
    def __init__(self):
        super().__init__('WorldBatch')

    def run(self):
        base_args = (self.config.source_dir, self.config.project_dir, self.config.platform)

        batch = []

        batch.extend([
            OdfMungeJob(['$*.odf'], *base_args),
            # ModelMungeJob(['$*.msh'], *base_args),
            # TextureMungeJob(['$*.tga', '$*.pic'], *base_args),
            # TerrainMungeJob(['$*.ter'], *base_args),
            WorldMungeJob(['$*.lyr'], *base_args),  # All non-base layers
            WorldMungeJob(['$*.wld'], *base_args),  # The base layer, ties it all together
        ])

        path_jobs = []
        for wld_file in self.config.source_dir.glob('**/*.wld'):
            path_jobs.append(ConfigMungeJob(['$*.pth'], *base_args, output_file=wld_file.stem.lower(),
                                            extension='.path', chunk_id='path'))
        batch.extend(path_jobs)

        batch.extend([
            PlanningMungeJob(['$*.pln'], *base_args),
            ConfigMungeJob(['$*.sky'], *base_args, chunk_id='sky'),
            ConfigMungeJob(['$*.fx'], *base_args, extension='.envfx', chunk_id='fx'),
            # ConfigMungeJob(['$*.prp'], *base_args, hash_strings=True, extension='.prop', chunk_id='prp'),
            # ConfigMungeJob(['$*.bnd'], *base_args, hash_strings=True, extension='.boundary', chunk_id='bnd'),
            # sound...
            ConfigMungeJob(['$*.lgt'], *base_args, extension='.light', chunk_id='lght'),
            ConfigMungeJob(['$*.pvs'], *base_args, extension='.povs', chunk_id='PORT'),
        ])

        self.job_runner.add_batch(batch)
        self.job_runner.start()
        self.job_runner.wait()
        self.logger.info('World {} done!'.format(self.config.source_dir.stem))
