import pathlib
import struct

from mungers.MungerBase import MungerBase
from mungers.ast.BarrierDoc import BarrierDoc
from mungers.ast.HintDoc import HintDoc
from mungers.ast.Region import Region
from mungers.ast.RegionDoc import RegionDoc
from mungers.ast.WorldDoc import WorldDoc

from mungers.parsers.ConfigParser import ConfigParser
from mungers.parsers.ParserOptions import ParserOptions
from util.string_util import str_in_i

CONFIG_SECTION_WHITELIST = {
    'Barrier',
    'Hint',
    'Object',
    'Region',
    'SkyName',
    'TerrainName',
}


class WorldMunge(MungerBase):
    def __init__(self):
        super().__init__('WorldMunge')

    def get_included_files(self, world_file: pathlib.Path) -> list[pathlib.Path]:
        parent = world_file.parent
        world_name = world_file.stem
        region_file = None
        hint_file = None
        barrier_file = None
        for file in parent.glob('{}.*'.format(world_name)):
            if str_in_i(file.suffix, '.rgn'):
                region_file = file
            if str_in_i(file.suffix, '.hnt'):
                hint_file = file
            if str_in_i(file.suffix, '.bar'):
                barrier_file = file
        return [region_file, hint_file, barrier_file]

    def run(self):
        extension = '.world'

        if not self.args.output_dir.exists():
            self.args.output_dir.mkdir(parents=True)

        input_files = self.get_input_files()

        if not input_files:
            self.logger.info('No input files were found. Stopping...')
            return

        world_parser_options = ParserOptions(document_cls=WorldDoc,
                                             all_numbers_are_floats=False,
                                             all_values_are_strings=True)
        world_parser = ConfigParser(world_parser_options)

        region_parser_options = ParserOptions(document_cls=RegionDoc,
                                              all_numbers_are_floats=False)
        region_parser = ConfigParser(region_parser_options)

        hint_parser_options = ParserOptions(document_cls=HintDoc,
                                            all_numbers_are_floats=False,
                                            all_values_are_strings=True)
        hint_parser = ConfigParser(hint_parser_options)

        barrier_parser_options = ParserOptions(document_cls=BarrierDoc,
                                               all_numbers_are_floats=False,
                                               all_values_are_strings=False)
        barrier_parser = ConfigParser(barrier_parser_options)

        self.logger.info('Parsing {} input files'.format(len(input_files)))
        world_file_parse_data_map = {input_file: world_parser.parse_file(input_file) for input_file in input_files}

        self.logger.info('Searching for .bar, .rgn, and .hnt files')
        world_file_include_file_map = {input_file: tuple(self.get_included_files(input_file))
                                       for input_file in input_files}

        world_file_region_size_binary_map = dict()
        world_file_hint_size_binary_map = dict()
        world_file_barrier_size_binary_map = dict()
        for world_file, include_files in world_file_include_file_map.items():
            region_file, hint_file, barrier_file = include_files
            if region_file is not None:
                self.logger.debug('Parsing region file {}'.format(region_file))
                region_parse_data = region_parser.parse_file(region_file)
                world_file_region_size_binary_map[world_file] = [
                    sum(1 for x in region_parse_data.instances if isinstance(x, Region)),
                    region_parse_data.to_binary()
                ]
            if hint_file is not None:
                self.logger.debug('Parsing hint file {}'.format(hint_file))
                hint_parse_data = hint_parser.parse_file(hint_file)
                world_file_hint_size_binary_map[world_file] = hint_parse_data.to_binary()
            if barrier_file is not None:
                self.logger.debug('Parsing barrier file {}'.format(barrier_file))
                barrier_parse_data = barrier_parser.parse_file(barrier_file)
                world_file_barrier_size_binary_map[world_file] = barrier_parse_data.to_binary()

        for file_path, parse_data in world_file_parse_data_map.items():
            parse_data.instances = [inst for inst in parse_data.instances if inst.name in CONFIG_SECTION_WHITELIST]
            #total_config_size = 0
            pack_str = '<4sI'
            raw_binaries = bytearray()

            self.logger.info('Munging {file}...'.format(file=file_path))
            config_name = file_path.stem
            parse_data.name = config_name
            region_data = world_file_region_size_binary_map[file_path]
            hint_binary = world_file_hint_size_binary_map[file_path]
            barrier_binary = world_file_barrier_size_binary_map[file_path]
            config_size, config_binary = parse_data.to_binary(region_data=region_data,
                                                              hint_binary=hint_binary,
                                                              barrier_binary=barrier_binary)
            #total_config_size += config_size  # TODO figure out why this is wrong
            raw_binaries.extend(config_binary)

            pack_str += '{}s'.format(len(raw_binaries))
            binary = struct.pack(pack_str, b'ucfb', len(raw_binaries), raw_binaries)
            root_config_file_name = pathlib.Path(config_name).with_suffix(extension)
            root_config_file_path = self.args.output_dir / root_config_file_name

            with open(root_config_file_path, 'wb') as f:
                num_written = f.write(binary)
                self.logger.info('Wrote {nbytes} bytes to {path}'.format(nbytes=num_written, path=root_config_file_path))
