from mungers.MungerBase import MungerBase
from mungers.ast.PathConfig import PathConfig
from mungers.util.config_parser import parse_config_file


class PathMunge(MungerBase):
    def __init__(self):
        super().__init__('PathMunge')

    def run(self):
        input_files = self.get_input_files()
        self.logger.info('Parsing {} input files'.format(len(input_files)))
        config_data = {input_file: parse_config_file(input_file, PathConfig) for input_file in input_files}
        for config, parse_data in config_data.items():
            config_name = config.stem

