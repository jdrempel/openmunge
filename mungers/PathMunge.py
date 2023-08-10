import pathlib
import struct

from mungers.MungerBase import MungerBase
from mungers.ast.PathConfig import PathConfig
from mungers.util.config_parser import parse_config_file


class PathMunge(MungerBase):
    def __init__(self):
        super().__init__('PathMunge')

    def run(self):
        input_files = self.get_input_files()
        self.logger.info('Parsing {} input files'.format(len(input_files)))
        file_parse_data_map = {input_file: parse_config_file(input_file, PathConfig) for input_file in input_files}
        total_config_size = 0
        binary = bytearray()
        binary.extend(b'ucfb')
        pack_str = '<4sI'
        raw_binaries = bytearray()
        for file_path, parse_data in file_parse_data_map.items():
            config_name = file_path.stem
            parse_data.name = config_name
            config_size, config_binary = parse_data.to_binary()
            total_config_size += config_size  # TODO figure out why this is wrong
            raw_binaries.extend(config_binary)
        pack_str += '{}s'.format(len(raw_binaries))
        binary = struct.pack(pack_str, b'ucfb', len(raw_binaries), raw_binaries)
        root_config_file_name = pathlib.Path(self.args.source_dir.stem).with_suffix('.path')
        with open(root_config_file_name, 'wb') as f:
            num_written = f.write(binary)
            self.logger.info('Wrote {nbytes} bytes to {path}'.format(nbytes=num_written, path=root_config_file_name))
