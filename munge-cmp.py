"""Compares two munged files to ensure they are near-identical, accounting for small differences in float values."""

import argparse
import pathlib
import subprocess
import sys


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('actual', type=pathlib.Path)
    parser.add_argument('golden', type=pathlib.Path)
    parser.add_argument('--atol',
                        type=float,
                        default=None,
                        help='The maximum absolute difference between two float values that permits the two values to '
                             'be considered identical. If --atol and --rtol are both used, both tolerances must be met '
                             'for two values to be identical. If neither one is used, two values must be exactly equal '
                             'to be identical.')
    parser.add_argument('--rtol',
                        type=float,
                        default=None,
                        help='The maximum relative difference between two float values that permits the two values to '
                             'be considered identical. Expressed as a decimal percent, with 1.0 being 100%. The exact '
                             'calculation for relative difference is abs(golden-actual)/golden. If --atol and --rtol '
                             'are both used, both tolerances must be met for two values to be identical. If neither '
                             'one is used, two values must be exactly equal to be identical.')
    args = parser.parse_args()
    return args


def validate_args(args):
    if not args.actual.exists():
        print('{} does not exist.'.format(args.actual))
        sys.exit(1)
    if not args.golden.exists():
        print('{} does not exist.'.format(args.golden))
        sys.exit(1)


def main():
    args = parse_args()
    validate_args(args)

    cmp_args = ['cmp', '-l', str(args.actual), str(args.golden)]
    process = subprocess.Popen(cmp_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outs, errs = process.communicate()
    process.wait()
    if process.returncode == 0:
        print('SUCCESS: Files are identical!')
        sys.exit(0)

    out_str = outs.decode('ascii')
    out_lines = [s.split() for s in out_str.split('\n') if s.strip()]
    out_data = [(int(a)-1, int('0'+b, 8), int('0'+c, 8)) for a, b, c in out_lines]
    index = 0
    while index < len(out_data):
        # noinspection PyUnusedLocal
        pos, actual, golden = out_data[index]
        # TODO
        index += 1


if __name__ == '__main__':
    main()
