import pathlib

from mungers.MungerBase import MungerBase
from mungers.ast.ConfigDoc import ConfigDoc
from mungers.chunks.Chunk import Chunk
from mungers.parsers.ConfigParser import ConfigParser
from mungers.parsers.ParserOptions import ParserOptions
from mungers.util.ReqDatabase import ReqDatabase
from util.config import Config


class CfgMungeConfig(Config):
    def setup_options(self):
        self.add_option('output_file',
                        show_in_cfg=False,
                        help='If specified, all intermediate munged output will be merged into a single file with '
                             'its name using the format: OUTPUT_FILE.EXT (see -ext/--extension).')
        self.add_option('extension',
                        alts=['-ext'],
                        show_in_cfg=False,
                        metavar='EXT',
                        help='The file extension to be given to intermediate munged files.')
        self.add_option('chunk_id',
                        metavar='ID',
                        required=True,
                        show_in_cfg=False,
                        help='If specified, override the IDs of all munged config chunks to have this value (must '
                             'be 4 ASCII characters or less).')


class ConfigMunge(MungerBase):
    def __init__(self):
        super().__init__('ConfigMunge')

    def create_script_config(self):
        script_config = CfgMungeConfig(self.name.lower())
        script_config.setup(self.arg_parser, args=self.job_args, only_known=True)
        return script_config

    def run(self):
        output_name = self.config.source_dir.stem.lower() if self.config.output_file is None \
            else self.config.output_file
        if self.config.extension is not None:
            extension = '.{}'.format(self.config.extension) if not self.config.extension.startswith('.') \
                else self.config.extension
        else:
            extension = '.config'

        parser_options = ParserOptions(document_cls=ConfigDoc)
        config_parser = ConfigParser(parser_options)
        self.logger.info('Parsing {} input files'.format(len(self.input_files)))
        file_parse_data_map = {input_file: config_parser.parse_file(input_file) for input_file in self.input_files}

        with Chunk('ucfb').open() as root:
            for file_path, config in file_parse_data_map.items():
                self.logger.info('Munging {file}...'.format(file=file_path))
                config_name = file_path.stem
                config.chunk_id = self.config.chunk_id
                config.config_name = config_name
                with config.open(root):
                    with Chunk('NAME').open(config) as name:
                        name.write_bytes(config.config_name)
                    for instance in config.instances:
                        instance.to_binary(config)

        root_config_file_name = pathlib.Path(output_name).with_suffix(extension)
        root_config_file_path = self.config.output_dir / root_config_file_name

        with open(root_config_file_path, 'wb') as f:
            num_written = f.write(root.binary)
            self.logger.info('Wrote {nbytes} bytes to {path}'.format(nbytes=num_written, path=root_config_file_path))

        self.logger.info('Finished munging files. Writing output...')
        db = ReqDatabase()

        req_file_path = pathlib.Path(str(root_config_file_path) + '.req')
        db.write(req_file_path)
        self.logger.debug('Wrote requirements db to {}'.format(req_file_path))
