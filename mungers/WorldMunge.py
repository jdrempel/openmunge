import pathlib

from mungers.MungerBase import MungerBase
from mungers.ast.Barrier import Barrier
from mungers.ast.GenericDoc import GenericDoc
from mungers.ast.Hint import Hint
from mungers.ast.Region import Region
from mungers.ast.WorldDoc import WorldDoc
from mungers.chunks.Chunk import Chunk

from mungers.parsers.ConfigParser import ConfigParser
from mungers.parsers.ParserOptions import ParserOptions
from mungers.util.ReqDatabase import ReqDatabase
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

    @staticmethod
    def get_included_files(world_file: pathlib.Path) -> list[pathlib.Path]:
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

        world_parser_options = ParserOptions(document_cls=WorldDoc,
                                             all_numbers_are_floats=False,
                                             all_values_are_strings=True)
        world_parser = ConfigParser(world_parser_options)

        region_parser_options = ParserOptions(document_cls=GenericDoc,
                                              all_numbers_are_floats=False)
        region_parser = ConfigParser(region_parser_options)

        hint_parser_options = ParserOptions(document_cls=GenericDoc,
                                            all_numbers_are_floats=False,
                                            all_values_are_strings=True)
        hint_parser = ConfigParser(hint_parser_options)

        barrier_parser_options = ParserOptions(document_cls=GenericDoc,
                                               all_numbers_are_floats=False,
                                               all_values_are_strings=False)
        barrier_parser = ConfigParser(barrier_parser_options)

        self.logger.info('Parsing {} input files'.format(len(self.input_files)))
        world_file_parse_data_map = {input_file: world_parser.parse_file(input_file) for input_file in self.input_files}

        self.logger.info('Searching for .bar, .rgn, and .hnt files')
        for input_file in self.input_files:
            includes = self.get_included_files(input_file)
            self.logger.info('Included files for {}: {}'.format(input_file, [str(x.name) for x in includes
                                                                             if x is not None]))
        world_file_include_file_map = {input_file: tuple(self.get_included_files(input_file))
                                       for input_file in self.input_files}

        for world_file, include_files in world_file_include_file_map.items():
            region_file, hint_file, barrier_file = include_files
            if region_file is not None:
                self.logger.debug('Parsing region file {}'.format(region_file))
                region_parse_data = region_parser.parse_file(region_file)
                world_file_parse_data_map[world_file].regions = [x for x in region_parse_data.instances if
                                                                 isinstance(x, Region)]
            if hint_file is not None:
                self.logger.debug('Parsing hint file {}'.format(hint_file))
                hint_parse_data = hint_parser.parse_file(hint_file)
                world_file_parse_data_map[world_file].hints = [x for x in hint_parse_data.instances if
                                                               isinstance(x, Hint)]
            if barrier_file is not None:
                self.logger.debug('Parsing barrier file {}'.format(barrier_file))
                barrier_parse_data = barrier_parser.parse_file(barrier_file)
                world_file_parse_data_map[world_file].barriers = [x for x in barrier_parse_data.instances if
                                                                  isinstance(x, Barrier)]

        for file_path, world in world_file_parse_data_map.items():
            self.logger.info('Munging {file}...'.format(file=file_path))
            world.instances = [inst for inst in world.instances if inst.name in CONFIG_SECTION_WHITELIST]
            with Chunk('ucfb') as root:
                with root.open(inst=world):
                    with world.open('NAME') as name:
                        name.write_str(file_path.stem.lower())
                    if world.terrain_name is not None:
                        with world.open('TNAM') as tnam:
                            tnam.write_str(world.terrain_name)
                    if world.sky_name is not None:
                        with world.open('SNAM') as snam:
                            snam.write_str(world.sky_name)
                    with world.open('INFO') as info:
                        info.write_int(len(world.regions))
                        info.write_int(len(world.instances))
                    for region in world.regions:
                        with world.open(inst=region):
                            with region.open('INFO') as info:
                                with info.open('TYPE') as type_:
                                    type_.write_str(region.region_type)
                                with info.open('NAME') as name:
                                    name.write_str(region.class_info)
                                with info.open('XFRM') as xfrm:
                                    for f in region.get_transform():
                                        xfrm.write_float(f)
                                with info.open('SIZE') as size:
                                    for f in region.size:
                                        size.write_float(f)
                            for prop in region.body:
                                if not str(prop.args[0]):
                                    continue
                                with region.open(inst=prop):
                                    prop.write_bytes(prop.name)
                                    prop.write_str(prop.args[0])
                    for instance in world.instances:
                        with world.open(inst=instance):
                            with instance.open('INFO') as info:
                                with info.open('TYPE') as type_:
                                    type_.write_str(instance.class_)
                                with info.open('NAME') as name:
                                    name.write_str(instance.label)
                                with info.open('XFRM') as xfrm:
                                    for f in instance.get_transform():
                                        xfrm.write_float(f)
                            for prop in instance.body:
                                if not str(prop.args[0]):
                                    continue
                                with instance.open(inst=prop):
                                    prop.write_bytes(prop.name)
                                    prop.write_str(prop.args[0])
                    for hint in world.hints:
                        with world.open(inst=hint):
                            with hint.open('INFO') as info:
                                with info.open('TYPE') as type_:
                                    type_.write_str(hint.hint_type)
                                with info.open('NAME') as name:
                                    name.write_str(hint.hint_name)
                                with info.open('XFRM') as xfrm:
                                    for f in hint.get_transform():
                                        xfrm.write_float(f)
                            for prop in hint.body:
                                if not str(prop.args[0]):
                                    continue
                                with hint.open(inst=prop):
                                    prop.write_bytes(prop.name)
                                    prop.write_str(prop.args[0])
                    for barrier in world.barriers:
                        with world.open(inst=barrier):
                            with barrier.open('INFO') as info:
                                with info.open('NAME') as name:
                                    name.write_str(barrier.barrier_name)
                                with info.open('XFRM') as xfrm:
                                    for f in barrier.get_transform():
                                        xfrm.write_float(f)
                                with info.open('SIZE') as size:
                                    for f in barrier.get_size():
                                        size.write_float(f)
                                with info.open('FLAG') as flag:
                                    flag.write_int(barrier.flags)

            config_name = file_path.stem
            root_config_file_name = pathlib.Path(config_name).with_suffix(extension)
            root_config_file_path = self.config.output_dir / root_config_file_name

            with open(root_config_file_path, 'wb') as f:
                num_written = f.write(root.binary)
                self.logger.info('Wrote {nbytes} bytes to {path}'
                                 .format(nbytes=num_written, path=root_config_file_path))

            self.logger.info('Finished munging files. Writing output...')
            db = ReqDatabase()

            db.get_section('light').append(world.get_light_name())
            db.get_section('terrain').append(world.get_terrain_name())
            db.get_section('config').append(world.get_sky_name())
            db.get_section('path').append(world.get_path_name())
            for instance in world.instances:
                db.get_section('class').append(instance.get_class_name())

            req_file_path = pathlib.Path(str(root_config_file_path) + '.req')
            if db.write(req_file_path):
                self.logger.debug('Wrote requirements db to {}'.format(req_file_path))
