import pathlib
import struct

from mungers.MungerBase import MungerBase
from mungers.util.config_parser import parse_config_file


class ConfigMunge(MungerBase):
    def __init__(self):
        super().__init__('ConfigMunge')

    def create_script_args(self):
        group = self.arg_parser.add_argument_group('Config Munge Options')
        group.add_argument('--output-file',
                           type=str,
                           default=None,
                           help='If specified, all intermediate munged output will be merged into a single file with '
                                'its name using the format: OUTPUT_FILE.EXT (see -ext/--extension).')
        group.add_argument('-ext', '--extension',
                           metavar='EXT',
                           type=str,
                           help='The file extension to be given to intermediate munged files.')
        group.add_argument('--chunk-id',
                           metavar='ID',
                           type=str,
                           default=None,
                           help='If specified, override the IDs of all munged config chunks to have this value (must '
                                'be 4 ASCII characters or less).')

    def run(self):
        output_name = self.args.source_dir.stem.lower() if self.args.output_file is None else self.args.output_file
        if self.args.extension is not None:
            extension = '.{}'.format(self.args.extension) if not self.args.extension.startswith('.') \
                else self.args.extension
        else:
            extension = '.config'

        if not self.args.output_dir.exists():
            self.args.output_dir.mkdir(parents=True)

        input_files = self.get_input_files()

        if not input_files:
            self.logger.info('No input files were found. Stopping...')
            return

        self.logger.info('Parsing {} input files'.format(len(input_files)))
        file_parse_data_map = {input_file: parse_config_file(input_file) for input_file in input_files}

        total_config_size = 0
        binary = bytearray()
        binary.extend(b'ucfb')
        pack_str = '<4sI'
        raw_binaries = bytearray()

        for file_path, parse_data in file_parse_data_map.items():
            self.logger.info('Munging {file}...'.format(file=file_path))
            if self.args.chunk_id is not None:
                parse_data.id = self.args.chunk_id  # TODO but what about the other case where it's not given??
            config_name = file_path.stem
            parse_data.name = config_name
            config_size, config_binary = parse_data.to_binary()
            total_config_size += config_size  # TODO figure out why this is wrong
            raw_binaries.extend(config_binary)

        pack_str += '{}s'.format(len(raw_binaries))
        binary = struct.pack(pack_str, b'ucfb', len(raw_binaries), raw_binaries)
        root_config_file_name = pathlib.Path(output_name).with_suffix(extension)
        root_config_file_path = self.args.output_dir / root_config_file_name

        with open(root_config_file_path, 'wb') as f:
            num_written = f.write(binary)
            self.logger.info('Wrote {nbytes} bytes to {path}'.format(nbytes=num_written, path=root_config_file_path))
