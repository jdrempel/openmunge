import configparser
import pathlib
from collections import defaultdict

from core.util.hashing import magic
from mungers.MungerBase import MungerBase
from mungers.chunks.Chunk import Chunk
from mungers.parsers.OdfParser import OdfParser
from util.constants import ODF_DELIMITERS, ODF_COMMENT_PREFIXES


class OdfMunge(MungerBase):
    def __init__(self):
        super().__init__('OdfMunge')

    def run(self):
        extension = '.class'

        def multi_dict():
            d = defaultdict(list)
            return d

        self.logger.info('Parsing {} input files'.format(len(self.input_files)))
        odf_parser = OdfParser()
        file_parse_data_map = {input_file: odf_parser.parse_file(input_file) for input_file in self.input_files}

        for file_path, odf_data in file_parse_data_map.items():
            self.logger.info('Munging {file}...'.format(file=file_path))
            odf_name = file_path.stem
            with Chunk('ucfb').open() as root:
                with Chunk('entc').open(root) as entity_class:
                    with Chunk('BASE').open(entity_class) as base:
                        base.write_str(odf_data['__class_name'])
                    with Chunk('TYPE').open(entity_class) as type_:
                        type_.write_str(odf_name)
                    for key, value in odf_data['Properties']:
                        with Chunk('PROP').open(entity_class) as prop:
                            prop.write_bytes(magic(key))
                            prop.write_str(value)

            output_file_name = pathlib.Path(odf_name).with_suffix(extension)
            output_file_path = self.args.output_dir / output_file_name

            with open(output_file_path, 'wb') as f:
                num_written = f.write(root.binary)
                self.logger.info('Wrote {nbytes} bytes to {path}'.format(nbytes=num_written, path=output_file_path))

            self.logger.info('Finished munging files.')
