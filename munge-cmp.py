"""Compares two munged files to ensure they are near-identical, accounting for small differences in float values."""

import argparse
import pathlib
import struct
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


def abs_diff(actual, golden):
    return abs(actual - golden)


def rel_diff(actual, golden):
    return abs(actual - golden) / golden


def main():
    args = parse_args()
    validate_args(args)

    cmp_args = ['cmp', '-l', str(args.actual), str(args.golden)]
    process = subprocess.Popen(cmp_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outs, errs = process.communicate()
    process.wait()
    if process.returncode == 0:
        sys.exit(0)

    if (asize := args.actual.stat().st_size) != (gsize := args.golden.stat().st_size):
        print(f'{args.actual} size={asize}  {args.golden} size={gsize}')

    out_str = outs.decode('ascii')
    out_lines = [s.split() for s in out_str.split('\n') if s.strip()]
    out_data = [(int(a)-1, int('0'+b, 8), int('0'+c, 8)) for a, b, c in out_lines]

    diffs_found = False
    with open(args.actual, 'rb') as actual_file, open(args.golden, 'rb') as golden_file:
        index = 0
        while index < len(out_data):
            # noinspection PyUnusedLocal
            pos, actual, golden = out_data[index]
            actual_file.seek(pos)
            golden_file.seek(pos)
            if pos == 4:
                actual_val = struct.unpack('<I', actual_file.read(4))[0]
                golden_val = struct.unpack('<I', golden_file.read(4))[0]
                print(f'{args.actual} {args.golden}  '
                      f'Actual sizebyte: {actual_val}  Golden sizebyte: {golden_val}')
            elif pos % 4 == 0:
                actual_val = struct.unpack('<f', actual_file.read(4))[0]
                golden_val = struct.unpack('<f', golden_file.read(4))[0]
                if args.atol is not None and abs_diff(actual_val, golden_val) > args.atol:
                    print(f'{args.actual} {args.golden}  '
                          f'Index: {pos}  Actual: {actual_val:.6f}  Golden: {golden_val:.6f}  '
                          f'Diff: {actual_val-golden_val}')
                    diffs_found = True
                if args.rtol is not None and (pd := rel_diff(actual_val, golden_val)) > args.rtol:
                    print(f'{args.actual} {args.golden}  '
                          f'Index: {pos}  Actual: {actual_val:.6f}  Golden: {golden_val:.6f}  '
                          f'% Diff: {pd*100.0:.3f}%')
                    diffs_found = True
            while out_data[index][0] < pos + 4:
                index += 1
                if index >= len(out_data):
                    break

    if diffs_found:
        sys.exit(1)


if __name__ == '__main__':
    main()
