from jobs.BatchJob import WorldBatchJob, CommonBatchJob, SideBatchJob, LocalizeBatchJob
from util.config import get_global_args
from util.constants import MUNGE_ALL


def get_common_jobs(args) -> list:
    source_dir = args.project_dir / 'Common'
    jobs = []
    if args.localize:
        loc_source_dir = source_dir / 'Localize'
        jobs = [LocalizeBatchJob(loc_source_dir.absolute(), args.project_dir, args.platform)]
    jobs.append(CommonBatchJob(source_dir.absolute(), args.project_dir, args.platform))

    return jobs


def get_side_jobs(args) -> list:
    jobs = []
    sides_dir = args.project_dir / 'Sides'

    if args.sides[0] == MUNGE_ALL:
        source_dirs = sorted(x.absolute() for x in sides_dir.iterdir() if x.is_dir())
        for source_dir in source_dirs:
            if source_dir.name == 'Common':
                # Common must come first if applicable
                jobs = [SideBatchJob(source_dir, args.project_dir, args.platform)] + jobs
                continue
            jobs.append(SideBatchJob(source_dir, args.project_dir, args.platform))
        return jobs

    source_dirs = sorted(x.absolute() for x in sides_dir.iterdir() if x.name.upper() in args.sides)
    common_sides_dir = sides_dir / 'Common'
    if common_sides_dir.exists():
        jobs = [SideBatchJob(common_sides_dir.absolute(), args.project_dir, args.platform)]
    for source_dir in source_dirs:
        jobs.append(SideBatchJob(source_dir, args.project_dir, args.platform))

    return jobs


def get_world_jobs(args) -> list:
    jobs = []
    worlds_dir = args.project_dir / 'Worlds'

    if args.worlds[0] == MUNGE_ALL:
        source_dirs = sorted(x.absolute() for x in worlds_dir.iterdir() if x.is_dir())
        for source_dir in source_dirs:
            if source_dir.name == 'Common':
                # Common must come first if applicable
                jobs = [WorldBatchJob(source_dir, args.project_dir, args.platform)] + jobs
                continue
            jobs.append(WorldBatchJob(source_dir, args.project_dir, args.platform))
        return jobs

    source_dirs = sorted(x.absolute() for x in worlds_dir.iterdir() if x.name.upper() in args.worlds)
    common_world_dir = worlds_dir / 'Common'
    if common_world_dir.exists():
        jobs = [WorldBatchJob(common_world_dir.absolute(), args.project_dir, args.platform)]
    for source_dir in source_dirs:
        jobs.append(WorldBatchJob(source_dir, args.project_dir, args.platform))

    return jobs


def get_work_batches() -> list:
    args = get_global_args()

    batches = []

    if args.common:
        batches.append(get_common_jobs(args))

    side_jobs = []
    if args.sides:
        side_jobs = get_side_jobs(args)

    world_jobs = []
    if args.worlds:
        world_jobs = get_world_jobs(args)

    if side_jobs and world_jobs:
        batches.append(side_jobs + world_jobs)
    elif side_jobs:
        batches.append(side_jobs)
    elif world_jobs:
        batches.append(world_jobs)

    return batches

