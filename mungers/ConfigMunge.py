import pathlib

from mungers.MungerBase import MungerBase
from mungers.ast.ConfigDoc import ConfigDoc
from mungers.chunks.Chunk import Chunk
from mungers.parsers.ConfigParser import ConfigParser
from mungers.parsers.ParserOptions import ParserOptions
from mungers.util.ReqDatabase import ReqDatabase


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

        parser_options = ParserOptions(document_cls=ConfigDoc)
        config_parser = ConfigParser(parser_options)
        self.logger.info('Parsing {} input files'.format(len(input_files)))
        file_parse_data_map = {input_file: config_parser.parse_file(input_file) for input_file in input_files}

        with Chunk('ucfb').open() as root:
            for file_path, config in file_parse_data_map.items():
                self.logger.info('Munging {file}...'.format(file=file_path))
                config_name = file_path.stem
                config.chunk_id = self.args.chunk_id
                config.config_name = config_name
                with config.open(root):
                    with Chunk('NAME').open(config) as name:
                        name.write_bytes(config.config_name)
                    for instance in config.instances:
                        instance.to_binary(config)

        root_config_file_name = pathlib.Path(output_name).with_suffix(extension)
        root_config_file_path = self.args.output_dir / root_config_file_name

        with open(root_config_file_path, 'wb') as f:
            num_written = f.write(root.binary)
            self.logger.info('Wrote {nbytes} bytes to {path}'.format(nbytes=num_written, path=root_config_file_path))

        self.logger.info('Finished munging files. Writing output...')
        db = ReqDatabase()

        req_file_path = pathlib.Path(str(root_config_file_path) + '.req')
        db.write(req_file_path)
        self.logger.debug('Wrote requirements db to {}'.format(req_file_path))
