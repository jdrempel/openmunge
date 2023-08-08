import pprint

from mungers.MungerBase import MungerBase
from mungers.util.config_parser import parse_config_file


class PathMunge(MungerBase):
    def __init__(self):
        super().__init__('PathMunge')

    def get_input_files(self):
        all_source_files = self.args.source_dir.glob('**/*')
        self.logger.info(list(all_source_files))
        all_source_files = list(self.args.source_dir.glob('**/*'))
        result = []
        for input_file_pattern in self.args.input_files:
            result.extend([file for file in all_source_files if file.suffix.lower() in input_file_pattern.lower() and file.is_file()])
        self.logger.info(result)
        return sorted(result)

    def run(self):
        self.logger.info('Sweet')
        input_files = self.get_input_files()
        config_data = {input_file: parse_config_file(str(input_file)) for input_file in input_files}
        cd = list(config_data.values())[-1]
        pass