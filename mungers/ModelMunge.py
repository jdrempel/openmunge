from core.config import Config
from mungers.MungerBase import MungerBase
from mungers.chunks.Chunk import Chunk
from mungers.parsers.MshParser import parse_msh_file


class ModelMungeConfig(Config):
    def setup_options(self):
        self.add_option('keep',
                        ['-keep'],
                        type=str,
                        help='Keep the named node as a hardpoint in the munged skeleton.')
        self.add_option('keep_all',
                        ['-keepall'],
                        type=bool,
                        help='Keep all nodes as hardpoints.')
        self.add_option('keep_material',
                        ['-keepmaterial'],
                        type=str,
                        help='Do not combine geometry attached to the named node with other geometry, so that it may '
                             'be accessed in-game to set material properties dynamically.')
        self.add_option('right_handed',
                        ['-righthanded'],
                        type=bool,
                        default=False,
                        help='Mirror Z axis to make axes right-handed (NOTE: This is deprecated for SWBFII).')
        self.add_option('left_handed',
                        ['-lefthanded'],
                        type=bool,
                        default=False,
                        help='Mirror Z axis to make axes left-handed.')
        self.add_option('scale',
                        ['-scale'],
                        type=float,
                        default=1.0,
                        help='Rescale the model by the given factor when munging. Default: {default}.')
        self.add_option('max_bones',
                        ['-maxbones'],
                        type=int,
                        default=16,
                        help='If the model is skinned, split the skinned segments up so that no segment accesses too '
                             'many bones. Default: {default}.')
        self.add_option('lod_group',
                        ['-lodgroup'],
                        type=str,
                        choices=('model', 'bigmodel', 'soldier', 'hugemodel'),
                        default='model',
                        help='Set the LOD group of the model to be one of (model, bigmodel, soldier, hugemodel). '
                             'Default: {default}.')
        self.add_option('lod_bias',
                        ['-lodbias'],
                        type=float,
                        default=1.0,
                        help='Set a bias on the distance at which the model will LOD. Larger values will cause the '
                             'model to remain detailed at greater distances. Default: {default}.')
        self.add_option('no_collision',
                        ['-nocollision'],
                        type=bool,
                        default=False,
                        help='Do not munge collision geometry for the model.')
        self.add_option('no_game_model',
                        ['-nogamemodel'],
                        type=bool,
                        default=False,
                        help='Do not export LOD data for this model.')
        self.add_option('hi_res_shadow',
                        ['-hiresshadow'],
                        type=int,
                        default=None,
                        help='Generate a shadow volume directly from the object geometry for the given LOD level, or '
                             '0 if no argument is given.')
        self.add_option('soft_skin_shadow',
                        ['-softskinshadow'],
                        type=bool,
                        default=False,
                        help='If the model has a skinned shadow volume, export full 3-bone skinning weights. NOTE: '
                             'This is expensive at runtime. Default behavior is to reduce all shadow volumes to hard '
                             'skinning (1 bone per vertex).')
        self.add_option('hard_skin_only',
                        ['-hardskinonly'],
                        type=bool,
                        default=False,
                        help='Force all skinned segments to 1-bone hard skinning.')
        self.add_option('soft_skin',
                        ['-softskin'],
                        type=bool,
                        default=False,
                        help='Export full 3-bone soft skinning weights for segments which are not explicitly hard-'
                             'skinned. Default behavior is hard skinning for fixed function, soft skinning for vertex '
                             'shader-enabled cards.')
        self.add_option('do_not_merge_skins',
                        ['-donotmergeskins'],
                        type=bool,
                        default=False,
                        help='If this option is not set, any model with at least one skinned segment will have all non-'
                             'skinned segments merged together into one hard skinned segment for performance reasons.')
        self.add_option('vertex_lighting',
                        ['-vertexlighting'],
                        type=bool,
                        default=False,
                        help='If the model has any geometry with vertex colors, interpret them as burned-in vertex '
                             'lighting. Default behavior is to interpret them as a modifier to the diffuse color of '
                             'the object.')
        self.add_option('additive_emissive',
                        ['-additiveemissive'],
                        type=bool,
                        default=False,
                        help='Interpret any materials in the model with the Lit checkbox unchecked as additive '
                             'blended.')
        self.add_option('bump',
                        ['-bump'],
                        type=str,
                        help='Any normal materials with a diffuse texture listed by name will be converted to use bump '
                             'mapping using the texture "<diffuse_name>_bump".')
        self.add_option('bounding_box_scale',
                        ['-boundingboxscale'],
                        type=float,
                        default=1.0,
                        help='Adjust the scale of the bounding box for the model by the given factor.')
        self.add_option('bounding_box_offset_x',
                        ['-boundingboxoffsetx'],
                        type=float,
                        default=0.0,
                        help='Adjust the location of the bounding box for the model by the given translation amount in '
                             'the X axis.')
        self.add_option('bounding_box_offset_y',
                        ['-boundingboxoffsety'],
                        type=float,
                        default=0.0,
                        help='Adjust the location of the bounding box for the model by the given translation amount in '
                             'the Y axis.')
        self.add_option('bounding_box_offset_z',
                        ['-boundingboxoffsetz'],
                        type=float,
                        default=0.0,
                        help='Adjust the location of the bounding box for the model by the given translation amount in '
                             'the +Z axis. For a negative Z offset use bounding_box_offset_nz.')
        self.add_option('bounding_box_offset_nz',
                        ['-boundingboxoffsetnz'],
                        type=float,
                        default=0.0,
                        help='Adjust the location of the bounding box for the model by the given translation amount in '
                             'the -Z axis. For a positive Z offset use bounding_box_offset_z.')
        self.add_option('k_collision',
                        ['-kcollision'],
                        type=bool,
                        default=False,
                        help='?')
        self.add_option('do_not_merge_collision',
                        ['-donotmergecollision'],
                        type=bool,
                        default=False,
                        help='?')
        self.add_option('remove_vertices_on_merge',
                        ['-removeverticesonmerge'],
                        type=bool,
                        default=False,
                        help='?')


class ModelMunge(MungerBase):
    def __init__(self):
        super().__init__('ModelMunge')

    def create_script_args(self):
        pass

    def create_script_config(self):
        script_config = ModelMungeConfig(self.name.lower())
        script_config.setup(self.arg_parser, args=self.job_args, only_known=True)
        return script_config

    def run(self):
        extension = '.model'

        self.logger.info(f'Parsing {len(self.input_files)} input files')
        file_parse_data_map = {input_file: parse_msh_file(input_file) for input_file in self.input_files}

        for input_file, msh_data in file_parse_data_map.items():
            msh_name = input_file.stem
            with Chunk('ucfb') as root:
                with root.open('skel') as skel:
                    pass
                for model in msh_data.models:
                    with root.open('modl') as modl:
                        with modl.open('NAME') as name:
                            name.write_str(msh_name)
                        with modl.open('VRTX') as vrtx:
                            vrtx.write_int(0)
                        with modl.open('NODE') as node:
                            node.write_int(0)
                        with modl.open('INFO') as info:
                            # TODO determine the actual meaning of these 4 ints
                            info.write_int(0)
                            info.write_int(0)
                            info.write_int(1)
                            info.write_int(0)
                            info.write_vec3(msh_data.scene_info.bounding_box.min)
                            info.write_vec3(msh_data.scene_info.bounding_box.max)
                            info.write_int(len(model.segments))
                            # TODO Figure out how to get this number
                            info.write_int(0)
                        for segment in model.segments:
                            with modl.open('segm') as segm:
                                with segm.open('INFO') as info:
                                    # TODO what do these numbers mean?
                                    info.write_int(5)
                                    info.write_int(24)
                                    info.write_int(67)
                                with segm.open('MTRL') as mtrl:
                                    # TODO what do these ones mean?
                                    mtrl.write_int(0)
                                    mtrl.write_bytes(b'\xFF'*8)
                                    mtrl.write_byte(0)
                                    mtrl.write_int(0)
                                    mtrl.write_int(0)
                                    mtrl.write_int(0)
                                with segm.open('RTYP') as rtyp:
                                    rtyp.write_str('Normal')
