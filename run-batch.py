import argparse
import importlib
import sys

from util.logs import setup_logger

log = setup_logger('run-batch')


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('name',
                            type=str,
                            help='Name of the batch script class to load. E.g. to load WorldBatchScript, call this '
                                 'script with name=world (case-insensitive).')
    meta_args, remaining_args = arg_parser.parse_known_args()
    batch_script_name = '{}BatchScript'.format(meta_args.name.capitalize())
    batch_script_module = 'batch.{}'.format(batch_script_name)
    mod = importlib.import_module(batch_script_module)
    batch_script_cls = getattr(mod, batch_script_name)
    if batch_script_cls is None:
        log.error('{} could not be found'.format(batch_script_name))
        sys.exit(1)
    batch_script = batch_script_cls()
    batch_script.init(args=remaining_args)
    batch_script.start()


if __name__ == '__main__':
    main()
