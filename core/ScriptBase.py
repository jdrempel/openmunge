import argparse
import os
import sys
from abc import abstractmethod

from core.config import get_global_config
from util.constants import ENV_VAR_PREFIX
from util.logs import setup_logger


class ScriptBase:
    def __init__(self, name: str):
        self.name = name
        self.logger = setup_logger(self.name)

        self.arg_parser = None
        self.job_args = None
        self.config = None

    @staticmethod
    def get_env_vars_strs():
        relevant_vars = [(k, v) for k, v in os.environ.items() if k.startswith(ENV_VAR_PREFIX)]
        if not relevant_vars:
            return ('N/A',)
        return ('{}={}'.format(k, v) for k, v in relevant_vars)

    def print_setup_info(self):
        self.logger.info('Starting {}...'.format(self.name))
        self.logger.info('{name} Setup:\n'
                         '\tConfig File: {config}\n'
                         '\tArgs: {args}\n'
                         '\tEnv: {env}'
                         .format(name=self.name, config=self.config.config_file, args=' '.join(sys.argv),
                                 env='; '.join(self.get_env_vars_strs())))

    @abstractmethod
    def create_base_args(self):
        ...

    def create_script_args(self):
        pass

    @abstractmethod
    def create_base_config(self):
        ...

    def create_script_config(self):
        pass

    def init(self, args=None):
        if not self.arg_parser:
            self.arg_parser = argparse.ArgumentParser()

        self.config = get_global_config()
        self.job_args = self.config.setup(self.arg_parser, args=args, only_known=True)
        self.create_base_args()
        self.config |= self.create_base_config()
        self.create_script_args()
        self.config |= self.create_script_config()

        self.logger.setLevel(self.config.log_level)
        for handler in self.logger.handlers:
            handler.setLevel(self.config.log_level)

    @abstractmethod
    def start(self):
        ...

