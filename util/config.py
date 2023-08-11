import configparser
import pathlib

_args_init = False
_config_init = False


class Globals:
    def __init__(self):
        self.initialized = False
        self.args = None
        self.config = configparser.ConfigParser()


g = Globals()


# TODO *******
# TODO Use a ChainMap to have a fallback mechanism for getting args -> config -> envvars -> defaults
# TODO *******
def get_global_args():
    if not g.initialized:
        raise ValueError('Globals have not yet been initialized')
    return g.args


def get_global_config(key: str):
    if not g.initialized:
        raise ValueError('Globals have not yet been initialized')
    if '.' not in key:
        raise ValueError('get_global_config("{0}"): "{0}" is not in the format SECTION.KEY'.format(key))
    section, option = key.split('.')
    return g.config.get(section, option)


def setup_global_args(args):
    global _args_init
    g.args = args
    _args_init = True
    g.initialized = _args_init and _config_init


def setup_global_config():
    global _config_init
    g.config.read_dict({'global': {'cwd': pathlib.Path.cwd()}})
    _config_init = True
    g.initialized = _args_init and _config_init


def write_config(path):
    with open(path, 'w') as cfg_file:
        g.config.write(cfg_file)
