import logging
from abc import abstractmethod

from util.config import setup_global_args, setup_global_config
from util.logs import setup_logger


class ScriptBase:
    def __init__(self, name: str):
        self.name = name
        self.logger = setup_logger(self.name)

        self.arg_parser = None
        self.args = None
        self.job_args = None

    @abstractmethod
    def create_base_args(self):
        """Must create an argparse.ArgumentParser instance for self.arg_parser"""
        ...

    def create_script_args(self):
        pass

    def init(self, args=None):
        if not self.arg_parser:
            self.create_base_args()
            self.create_script_args()
        if args is None:
            self.args, self.job_args = self.arg_parser.parse_known_args()
        else:
            self.args, self.job_args = self.arg_parser.parse_known_args(args=args)
        setup_global_args(self.args)
        setup_global_config()

        self.logger.setLevel(self.args.log_level)
        for handler in self.logger.handlers:
            handler.setLevel(self.args.log_level)

    @abstractmethod
    def start(self):
        ...

