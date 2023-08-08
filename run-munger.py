import argparse
import importlib
import sys

from util.logs import setup_logger

log = setup_logger('run-munger')


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('name',
                            type=str,
                            help='Name of the munger class to load. E.g. to load ConfigMunger call this '
                                 'script with name=config (case-insensitive).')
    meta_args, remaining_args = arg_parser.parse_known_args()
    munger_name = '{}Munge'.format(meta_args.name.capitalize())
    munger_module = 'mungers.{}'.format(munger_name)
    mod = importlib.import_module(munger_module)
    munger_cls = getattr(mod, munger_name)
    if munger_cls is None:
        log.error('{} could not be found'.format(munger_name))
        sys.exit(1)
    munger = munger_cls()
    munger.init(args=remaining_args)
    munger.start()


if __name__ == '__main__':
    main()
