import argparse
import configparser as cfgp
import os
import pathlib
from collections import ChainMap

from util.arg_parsing import PositiveNumberArgumentType
from util.constants import Platform, ALL_PLATFORMS, ENV_VAR_PREFIX


class Globals:
    def __init__(self):
        self._initialized = False

        self._options = dict()
        self._defaults = dict()
        self._parsed_options = ChainMap()
        self._config_parser = cfgp.ConfigParser()

        self.setup_options()
        self.generate_defaults()

    def __getattr__(self, item):
        if not self._initialized:
            raise ValueError('Cannot __getattr__ on global config before it has been initialized.')
        try:
            return self._parsed_options[item]
        except KeyError:
            raise AttributeError('No option "{}" found in global options.'.format(item))

    def finish_init(self):
        self._initialized = True

    def add_option(self, name: str, alts=None, required=False, type=None, choices=None, dest=None, metavar=None,
                   default=None, help=None, sections=None, show_in_cli=True, show_in_cfg=True):
        """
        Add a new option to the _options dict for handling by the various config sources (CLI, config, env, defaults)
        :param name: The base name of the option, lowercase with underscores delimiting words, e.g. my_fun_option
        :param alts: A list of alternative flags to be used in the CLI form of the option (if applicable)
        :param required: When True, this option must be explicitly given on the CLI as an arg
        :param type: The type to which input values for this option will be coerced
        :param choices: A list or tuple or valid choices for inputs to this option
        :param dest: The code name for this option after parsing into the config namespace
        :param metavar: An alternative display name for this option in help text
        :param default: The default value if no input is given (if ``required=True``, this does nothing)
        :param help: Help text to be displayed when using -h on the command line
        :param sections: A list of section names under which this option can be used in the config file
        :param show_in_cli: When True, this option will be accessible as a CLI arg (must be True with ``required=True``)
        :param show_in_cfg: When True, this option will be accessible as a config file option
        :return: None
        """
        if required:
            assert show_in_cli, 'Option "{}" is required but show_in_cli is False.'.format(name)

        if dest is None:
            dest = name

        new_option = dict(name=name,
                          alts=alts,
                          required=required,
                          type=type,
                          choices=choices,
                          dest=dest,
                          metavar=metavar,
                          default=default,
                          help=help,
                          sections=sections,
                          show_in_cli=show_in_cli,
                          show_in_cfg=show_in_cfg)

        if name in self._options:
            raise KeyError('An option named {} already exists.'.format(name))

        for option in self._options.values():
            if option['dest'] == dest:
                raise KeyError('An option with dest {} already exists.'.format(dest))

        self._options[name] = new_option

    def setup_options(self):
        self.add_option('platform',
                        alts=['-p'],
                        metavar='PLATFORM',
                        type=Platform,
                        choices=ALL_PLATFORMS,
                        default=Platform.PC,
                        sections=['global'],
                        help='The platform to target for munging files. Choices: %(choices)s. Default: {default}.')

        self.add_option('project_dir',
                        alts=['-P'],
                        type=pathlib.Path,
                        sections=['global'],
                        help='The location of the project data to be munged. This should point to the data_ABC '
                             'directory (assuming ABC is the 3-letter code for the project).')

        self.add_option('config_file',
                        type=pathlib.Path,
                        default=pathlib.Path.home() / '.mungerc',
                        show_in_cfg=False,
                        help='Location of a config file to use for global options. Command-line options take precedent '
                             'over option values read from this file. Default: {default}')

        self.add_option('log_level',
                        alts=['-ll'],
                        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'),
                        default='INFO',
                        sections=['global'],  # TODO add sections for batch and mungers?
                        help='The minimum level of log message to be displayed. Choices: %(choices)s. '
                             'Default: {default}.')

        self.add_option('swbf2_path',
                        type=pathlib.Path,
                        sections=['global'],
                        help='Location of the SWBF2 installation where fully munged files will be copied. This should '
                             'point to the GameData directory.')

        self.add_option('max_concurrent_jobs',
                        metavar='NUM_JOBS',
                        type=PositiveNumberArgumentType(),
                        help='The number of munge jobs that can be run simultaneously. If left unspecified, will '
                             'default to the number of CPUs available.')

    def generate_defaults(self):
        for name, opt in self._options.items():
            if opt['required']:
                continue
            if name in self._defaults:
                raise KeyError('A default value for option {} has already been provided.'.format(name))
            self._defaults[opt['dest']] = opt['default']
        self._parsed_options.maps.clear()
        self._parsed_options.maps.append(self._defaults)

    def add_options_to_arg_parser(self, group):
        for opt in self._options.values():
            if not opt['show_in_cli']:
                continue
            argument_name = '--{}'.format(opt['name'].lower().replace('_', '-'))
            argument_args = [argument_name]
            if opt['alts']:
                argument_args.extend(opt['alts'])
            argument_kwargs = {key: opt[key] for key in
                               ('type', 'required', 'choices', 'dest', 'metavar', 'default', 'help')}
            argument_kwargs['default'] = None  # Because we defer default-handling to a lower level of config
            argument_kwargs['help'] = argument_kwargs['help'].format(default=self._defaults.get(opt['name']))
            group.add_argument(*argument_args, **argument_kwargs)

    def parse_cli_args(self, parser, args=None):
        namespace = parser.parse_args(args)
        cli_args = {k: v for k, v in vars(namespace).items() if v is not None}
        self._parsed_options = self._parsed_options.new_child(cli_args)

    def parse_cfg_file(self):
        cfg_file_path = self._parsed_options['config_file']
        if not cfg_file_path:
            raise AttributeError('No value for config_file found in globals (even in defaults!).')
        read_files = self._config_parser.read(cfg_file_path)
        if not read_files:
            raise IOError('Unable to read {}, no config data is available.'.format(str(cfg_file_path)))
        cfg_options = {k: v for k, v in self._config_parser.items('global')}

        # We now have to insert the config file options between env vars and cli args for precedence-preserving reasons
        maps = self._parsed_options.maps
        cli_args = maps[0]
        self._parsed_options = self._parsed_options.parents.new_child(cfg_options).new_child(cli_args)

    def parse_env_vars(self):
        env_vars = dict()
        for opt in self._options.values():
            if opt['required']:
                continue
            env_var_name = ENV_VAR_PREFIX + opt['name'].upper()
            if env_var_name not in os.environ:
                continue
            env_vars[opt['dest']] = opt['type'](os.environ[env_var_name])
        # We also inject the cwd
        env_vars['cwd'] = pathlib.Path(os.environ.get('PWD'))
        self._parsed_options = self._parsed_options.new_child(env_vars)


_global_config = Globals()


def get_global_config():
    return _global_config


def setup_global_config(cli_arg_group):
    _global_config.add_options_to_arg_parser(cli_arg_group)

    _global_config.parse_env_vars()
    _global_config.parse_cli_args(cli_arg_group)
    _global_config.parse_cfg_file()  # After cli args because the CLI args might tell us where to look for the config file

    _global_config.finish_init()
    return _global_config


if __name__ == '__main__':
    import sys
    os.environ.update({'MUNGE_CONFIG_FILE': '/home/jeremy/.mungerc'})
    sys.argv.extend(['--project-dir', '/foo/bar'])
    parser = argparse.ArgumentParser()
    setup_global_config(parser)

    global_config = get_global_config()

    print(_global_config.cwd)
    print(_global_config.swbf2_path)
    print(_global_config.project_dir)
    print(_global_config.max_concurrent_jobs)
