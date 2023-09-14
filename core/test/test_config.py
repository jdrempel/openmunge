import argparse
import os
import pathlib
import unittest
from importlib import reload
from unittest.mock import MagicMock, patch

import core
from core.config import get_global_config, setup_global_config


class ConfigTest(unittest.TestCase):
    def setUp(self) -> None:
        self.data_dir = self.get_data_dir('data')
        self.arg_parser = MagicMock(spec=argparse.ArgumentParser)

    def tearDown(self) -> None:
        reload(core.config)

    @staticmethod
    def get_data_dir(name: str):
        return pathlib.Path(__file__).parent / name

    def test_global_config_initialized(self):
        config = get_global_config()
        self.assertFalse(config.is_initialized())
        setup_global_config(self.arg_parser)
        self.assertTrue(config.is_initialized())

    def test_global_config_setup_env_var(self):
        """
        Tests that the global config sets itself up correctly when using an environment variable.
        """
        with patch.dict(os.environ, {'MUNGE_CONFIG_FILE': str(self.data_dir / 'basic.mungerc')}):
            config = setup_global_config(self.arg_parser)

        self.assertEqual(config.swbf2_path, pathlib.Path('/path/to/swbf2/gamedata'))
        self.assertEqual(config.platform, config.defaults['platform'])
        self.assertEqual(config.log_level, config.defaults['log_level'])
        self.assertEqual(config.project_dir, config.defaults['project_dir'])
        self.assertEqual(config.config_file, self.data_dir / 'basic.mungerc')

    def test_global_config_setup_cli_args(self):
        """
        Tests that the global config sets itself up correctly when using CLI args.
        """
        args = ['--config-file', self.data_dir / 'basic.mungerc']
        self.arg_parser.parse_args.return_value = argparse.Namespace(config_file=args[1])

        config = setup_global_config(self.arg_parser, args=args)

        self.assertEqual(config.swbf2_path, pathlib.Path('/path/to/swbf2/gamedata'))
        self.assertEqual(config.platform, config.defaults['platform'])
        self.assertEqual(config.log_level, config.defaults['log_level'])
        self.assertEqual(config.project_dir, config.defaults['project_dir'])
        self.assertEqual(config.config_file, self.data_dir / 'basic.mungerc')

    def test_global_config_precedence(self):
        """
        Checks that the order of precedence is CLI ARGS -> CONFIG FILE -> ENVIRONMENT -> DEFAULTS.
        """
        args = ['--platform', 'pc']
        self.arg_parser.parse_args.return_value = argparse.Namespace(platform=args[1])

        env_patch = {
            'MUNGE_PLATFORM': 'ps2',
            'MUNGE_CONFIG_FILE': str(self.data_dir / 'precedence.mungerc'),
            'MUNGE_LOG_LEVEL': 'ERROR',
        }
        with patch.dict(os.environ, env_patch):
            config = setup_global_config(self.arg_parser, args=args)

        self.assertEqual(config.platform, 'pc')  # From cli args
        self.assertEqual(config.project_dir, pathlib.Path('/config/file/project'))  # From config file
        self.assertEqual(config.log_level, 'ERROR')  # From environment
        self.assertEqual(config.swbf2_path, None)  # From defaults

    def test_config_file_choices_type(self):
        """
        Tests that config file options raise an error if their values cannot be coerced to the specified type.
        """
        with patch.dict(os.environ, {'MUNGE_CONFIG_FILE': str(self.data_dir / 'choices.type.mungerc')}):
            with self.assertRaises(ValueError) as cm:
                setup_global_config(self.arg_parser)
                self.assertEqual(cm.exception.args[0], 'switch is not a valid Platform')

    def test_config_file_choices_value(self):
        """
        Tests that config file options raise an error if their values are not in the set of allowed choices.
        """
        with patch.dict(os.environ, {'MUNGE_CONFIG_FILE': str(self.data_dir / 'choices.value.mungerc')}):
            with self.assertRaises(ValueError) as cm:
                setup_global_config(self.arg_parser)
                self.assertEqual(cm.exception.args[0], 'Option log_level=GARBAGE is not in valid set of choices '
                                                       '(DEBUG, INFO, WARNING, ERROR, CRITICAL)')

    def test_env_var_choices_type(self):
        """
        Tests that env var options raise an error if their values cannot be coerced to the specified type.
        """
        with patch.dict(os.environ, {'MUNGE_PLATFORM': 'switch'}):
            with self.assertRaises(ValueError) as cm:
                setup_global_config(self.arg_parser)
                self.assertEqual(cm.exception.args[0], 'switch is not a valid Platform')

    def test_env_var_choices_value(self):
        """
        Tests that env var options raise an error if their values are not in the set of allowed choices.
        """
        with patch.dict(os.environ, {'MUNGE_LOG_LEVEL': 'GARBAGE'}):
            with self.assertRaises(ValueError) as cm:
                setup_global_config(self.arg_parser)
                self.assertEqual(cm.exception.args[0], 'Option log_level=GARBAGE is not in valid set of choices '
                                                       '(DEBUG, INFO, WARNING, ERROR, CRITICAL)')
