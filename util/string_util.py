import argparse
import shlex


def pretty_print_args(args: argparse.Namespace) -> str:
    fmt = '--{name} {value}'
    res = []

    def stringify_list(x):
        if not isinstance(x, list):
            return x
        return shlex.join([str(v) for v in x])

    for dest, value in vars(args).items():
        if isinstance(value, bool) and not value:
            # Don't include 'store_true' args if they haven't been set
            continue
        if isinstance(value, list):
            value = stringify_list(value)
        s = fmt.format(name=dest.lower().replace('_', '-'), value=value)
        res.append(s)
    return ' '.join(res)
