import pathlib

from mungers.MungerBase import MungerBase
from mungers.ast.PlanningDoc import PlanningDoc
from mungers.chunks.Chunk import Chunk
from mungers.parsers.ConfigParser import ConfigParser
from mungers.parsers.ParserOptions import ParserOptions


class PlanningMunge(MungerBase):
    def __init__(self):
        super().__init__('PathPlanningMunge')

    def run(self):
        output_name = self.args.source_dir.stem
        extension = '.congraph'

        if not self.args.output_dir.exists():
            self.args.output_dir.mkdir(parents=True)

        input_files = self.get_input_files()

        if not input_files:
            self.logger.info('No input files were found. Stopping...')
            return

        parser_options = ParserOptions(document_cls=PlanningDoc)
        config_parser = ConfigParser(parser_options)
        self.logger.info('Parsing {} input files'.format(len(input_files)))
        file_parse_data_map = {input_file: config_parser.parse_file(input_file) for input_file in input_files}

        for file_path, plan in file_parse_data_map.items():
            self.logger.info('Munging {file}...'.format(file=file_path))
            config_name = file_path.stem
            with Chunk('ucfb').open() as root:
                with plan.open(root):
                    with Chunk('INFO').open(plan) as info:
                        info.write_short(len(plan.hubs))
                        info.write_short(len(plan.connections))
                        info.write_short(5)  # Num weights
                    with Chunk('NODE').open(plan) as node:
                        for hub in plan.hubs:
                            hub.to_binary(node, plan)
                    with Chunk('ARCS').open(plan) as arcs:
                        for connection in plan.connections:
                            connection.to_binary(arcs, plan)

            root_config_file_name = pathlib.Path(output_name).with_suffix(extension)
            root_config_file_path = self.args.output_dir / root_config_file_name

            with open(root_config_file_path, 'wb') as f:
                num_written = f.write(root.binary)
                self.logger.info('Wrote {nbytes} bytes to {path}'.format(nbytes=num_written, path=root_config_file_path))

            self.logger.info('Finished munging files.')
