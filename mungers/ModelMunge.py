from mungers.MungerBase import MungerBase
from mungers.parsers.msh_parsing import parse_msh_file


class ModelMunge(MungerBase):
    def __init__(self):
        super().__init__('ModelMunge')

    def create_script_args(self):
        pass

    def create_script_config(self):
        pass

    def run(self):
        extension = '.model'

        self.logger.info(f'Parsing {len(self.input_files)} input files')
        file_parse_data_map = {input_file: parse_msh_file(input_file) for input_file in self.input_files}
