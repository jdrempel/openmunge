import pathlib

from core.util.hashing import magic
from mungers.MungerBase import MungerBase
from mungers.chunks.Chunk import Chunk
from mungers.parsers.OdfParser import OdfParser


class OdfMunge(MungerBase):
    def __init__(self):
        super().__init__('OdfMunge')

    def run(self):
        extension = '.class'

        self.logger.info('Parsing {} input files'.format(len(self.input_files)))
        odf_parser = OdfParser()
        file_parse_data_map = {input_file: odf_parser.parse_file(input_file) for input_file in self.input_files}

        for file_path, odf_data in file_parse_data_map.items():
            self.logger.info('Munging {file}...'.format(file=file_path))
            odf_name = file_path.stem
            with Chunk('ucfb').open() as root:
                if odf_data.get('WeaponClass') is not None:
                    class_chunk_name = 'wpnc'
                elif odf_data.get('OrdnanceClass') is not None:
                    class_chunk_name = 'ordc'
                elif odf_data.get('ExplosionClass') is not None:
                    class_chunk_name = 'expc'
                else:
                    class_chunk_name = 'entc'
                with Chunk(class_chunk_name).open(root) as class_chunk:
                    with Chunk('BASE').open(class_chunk) as base:
                        base.write_str(odf_data['__class_name'])
                    with Chunk('TYPE').open(class_chunk) as type_:
                        type_.write_str(odf_name)
                    for key, value in odf_data['Properties']:
                        with Chunk('PROP').open(class_chunk) as prop:
                            prop.write_bytes(magic(key))
                            prop.write_str(value)

            output_file_name = pathlib.Path(odf_name).with_suffix(extension)
            output_file_path = self.args.output_dir / output_file_name

            with open(output_file_path, 'wb') as f:
                num_written = f.write(root.binary)
                self.logger.info('Wrote {nbytes} bytes to {path}'.format(nbytes=num_written, path=output_file_path))

            self.logger.info('Finished munging files.')
