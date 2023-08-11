import pathlib
import struct

from mungers.MungerBase import MungerBase
from mungers.util.config_parser import parse_config_file

CONFIG_SECTION_WHITELIST = {
    'Barrier',
    'Hint',
    'Object',
    'Region',
}


class WorldMunge(MungerBase):
    def __init__(self):
        super().__init__('WorldMunge')

    def run(self):
        extension = '.world'

        if not self.args.output_dir.exists():
            self.args.output_dir.mkdir(parents=True)

        input_files = self.get_input_files()

        if not input_files:
            self.logger.info('No input files were found. Stopping...')
            return

        self.logger.info('Parsing {} input files'.format(len(input_files)))
        file_parse_data_map = {input_file: parse_config_file(input_file) for input_file in input_files}

        for file_path, parse_data in file_parse_data_map.items():
            file_stem = file_path.stem
            parse_data.instances = [inst for inst in parse_data.instances if inst.name in CONFIG_SECTION_WHITELIST]
            continue
            #total_config_size = 0
            #pack_str = '<4sI'
            #raw_binaries = bytearray()

            #self.logger.info('Munging {file}...'.format(file=file_path))
            #parse_data.id = 'wrld'
            #config_name = file_path.stem
            #parse_data.name = config_name
            #config_size, config_binary = parse_data.to_binary()
            #total_config_size += config_size  # TODO figure out why this is wrong
            #raw_binaries.extend(config_binary)

            #pack_str += '{}s'.format(len(raw_binaries))
            #binary = struct.pack(pack_str, b'ucfb', len(raw_binaries), raw_binaries)
            #root_config_file_name = pathlib.Path(config_name).with_suffix(extension)
            #root_config_file_path = self.args.output_dir / root_config_file_name

            #with open(root_config_file_path, 'wb') as f:
            #    num_written = f.write(binary)
            #    self.logger.info('Wrote {nbytes} bytes to {path}'.format(nbytes=num_written, path=root_config_file_path))
