from core.types.material import MaterialData, MaterialAttributes, Material
from core.types.model import BoundingBox, SceneInfo, Model, GeometrySegment, ModelTransform, CollisionPrimitive, \
    Geometry
from mungers.util.BinaryReader import BinaryReader


class MshParser:
    def __init__(self, path):
        self.path = path

        self.scene_info = None
        self.is_shadow_mesh = False
        self.materials = []
        self.models = []

    @staticmethod
    def parse_tri_strips(strp_chunk, num_indices):
        strip_start = 0x8000
        tri_strips = []
        strip_buffer = []
        for i in range(num_indices):
            index = strp_chunk.read_u16()
            if index & strip_start:
                if len(strip_buffer) > 2:
                    tri_strips.append(strip_buffer)
                    strip_buffer = []
                elif len(strip_buffer) == 2:
                    raise ValueError(f'Tri strip short #{i} has a START_OF_STRIP bit but is immediately preceded by '
                                     f'two others. This should not happen.')
            strip_buffer.append(index & 0x7FFF)
        if strip_buffer:
            tri_strips.append(strip_buffer)
        return tri_strips

    def parse_mesh(self, chunk):
        while chunk.could_have_child():
            msh2_next_header = chunk.check_next_header()

            if msh2_next_header == 'SINF':
                with chunk.read_child() as sinf:
                    self.parse_scene_info(sinf)

            elif msh2_next_header == 'CAMR':
                if chunk.check_next_header() == 'CAMR':
                    with chunk.read_child() as camr:
                        chunk.skip(camr.size)

            elif msh2_next_header == 'MATL':
                with chunk.read_child() as matl:
                    self.parse_materials_list(matl)

            elif msh2_next_header == 'MODL':
                with chunk.read_child() as modl:
                    self.models.append(self.parse_model(modl))

            else:
                raise ValueError(f'Invalid chunk name encountered in MSH2: '
                                 f'"{msh2_next_header}"')

    def parse(self):
        with self.path.open('rb') as f:
            with BinaryReader(f) as file_root:
                with file_root.read_child() as hedr:

                    while hedr.could_have_child():
                        hedr_next_header = hedr.check_next_header()

                        if hedr_next_header == 'SHVO':
                            with hedr.read_child() as shvo:
                                has_shadow_volume = bool(shvo.read_u32())

                        elif hedr_next_header == 'MSH2':
                            with hedr.read_child() as msh2:
                                self.parse_mesh(msh2)

                        elif hedr_next_header == 'BLN2':
                            with hedr.read_child() as bln2:
                                pass

                        elif hedr_next_header == 'ANM2':
                            with hedr.read_child() as anm2:
                                pass

                        elif hedr_next_header == 'SKL2':
                            with hedr.read_child() as skl2:
                                pass

                        elif hedr_next_header == 'CL1L':
                            with hedr.read_child() as cl1l:
                                pass
                            # CL1L marks end of file
                            break

                        else:
                            raise ValueError(f'Unexpected chunk {hedr_next_header} found in HEDR at position '
                                             f'{hedr.get_position()}')

    def parse_scene_info(self, scene_info_chunk):
        with scene_info_chunk.read_child() as name:
            scene_name = name.read_str()

        with scene_info_chunk.read_child() as fram:
            start_frame = fram.read_u32()
            end_frame = fram.read_u32()
            frame_rate = fram.read_f32()

        with scene_info_chunk.read_child() as bbox:
            bounding_box = BoundingBox(
                rotation=bbox.read_quat(),
                origin=bbox.read_vec3(),
                extents=bbox.read_vec3(),
                sphere_radius=bbox.read_f32()
            )

        self.scene_info = SceneInfo(scene_name, start_frame, end_frame, frame_rate, bounding_box)

    def parse_materials_list(self, materials_list_chunk):
        num_materials = materials_list_chunk.read_u32()
        while materials_list_chunk.could_have_child() and materials_list_chunk.check_next_header() == 'MATD':
            if len(self.materials) == num_materials:
                break

            with materials_list_chunk.read_child() as matd:
                with matd.read_child() as name:
                    material_name = name.read_str()

                with matd.read_child() as data:
                    material_data = MaterialData(
                        diffuse=data.read_vec4(),
                        specular=data.read_vec4(),
                        ambient=data.read_vec4(),
                        sharpness=data.read_f32()
                    )

                with matd.read_child() as atrb:
                    material_attributes = MaterialAttributes(
                        flags=atrb.read_u8(),
                        render_type=atrb.read_u8(),
                        data=tuple([atrb.read_u8(), atrb.read_u8()])
                    )

                texture_names = []
                while matd.check_next_header().startswith('TX'):
                    if len(texture_names) == 4:
                        break
                    with matd.read_child() as tx_d:
                        texture_name = tx_d.read_str()
                        texture_names.append(texture_name)

                material = Material(material_name, material_data, material_attributes, texture_names)
                self.materials.append(material)

    def parse_segment(self, segment_chunk, materials_list):
        if segment_chunk.check_next_header() == 'SHDW':
            self.is_shadow_mesh = True
            pass

        if segment_chunk.check_next_header() == 'MATI':
            with segment_chunk.read_child() as mati:
                material_index = mati.read_u32()

        coordinates = []
        if not self.is_shadow_mesh:
            with segment_chunk.read_child() as posl:
                num_coordinates = posl.read_u32()
                coordinates.append(posl.read_vec3(num_coordinates))

        colours = []
        if segment_chunk.check_next_header() == 'CLRL':
            with segment_chunk.read_child() as clrl:
                pass

        if segment_chunk.check_next_header() == 'CLRB':
            with segment_chunk.read_child() as clrb:
                pass

        weights = []
        if segment_chunk.check_next_header() == 'WGHT':
            with segment_chunk.read_child() as wght:
                pass

        normals = []
        if not self.is_shadow_mesh:
            with segment_chunk.read_child() as nrml:
                num_normals = nrml.read_u32()
                normals.append(nrml.read_vec3(num_normals))

        uvs = []
        if segment_chunk.check_next_header() == 'UV0L':
            with segment_chunk.read_child() as uv0l:
                num_uvs = nrml.read_u32()
                uvs.append(nrml.read_vec2(num_uvs))

        polys = []
        if segment_chunk.check_next_header() == 'NDXL':
            with segment_chunk.read_child() as ndxl:
                pass

        tris = []
        if segment_chunk.check_next_header() == 'NDXT':
            with segment_chunk.read_child() as ndxt:
                pass

        tri_strips = []
        if segment_chunk.check_next_header() == 'STRP':
            with segment_chunk.read_child() as strp:
                num_indices = strp.read_u32()
                tri_strips = self.parse_tri_strips(strp, num_indices)

        geometry_segment = GeometrySegment(
            material_name=materials_list[material_index].name,
            positions=coordinates,
            normals=normals,
            colours=colours,
            uvs=uvs,
            weights=weights,
            polygons=polys,
            tris=tris,
            tri_strips=tri_strips
        )
        return geometry_segment

    def parse_model(self, model_header_chunk):
        model_name = None
        if model_header_chunk.check_next_header() == 'NAME':
            with model_header_chunk.read_child() as name:
                model_name = name.read_str()

        with model_header_chunk.read_child() as mtyp:
            model_type = mtyp.read_u32()

        with model_header_chunk.read_child() as mndx:
            model_index = mndx.read_u32()

        if model_header_chunk.check_next_header() == 'PRNT':
            with model_header_chunk.read_child() as prnt:
                model_parent = prnt.read_str()
                prnt.align()

        with model_header_chunk.read_child() as flgs:
            render_flags = flgs.read_u32()

        with model_header_chunk.read_child() as tran:
            model_transform = ModelTransform(
                scale=tran.read_vec3(),
                rotation=tran.read_quat(),
                translation=tran.read_vec3()
            )

        collision_primitives = []
        while model_header_chunk.check_next_header() == 'SWCI':
            with model_header_chunk.read_child() as swci:
                primitive = CollisionPrimitive(
                    shape=swci.read_s32(),
                    radius=swci.read_f32(),
                    height=swci.read_f32(),
                    length=swci.read_f32()
                )
                collision_primitives.append(primitive)

        geometry_list = []
        while model_header_chunk.check_next_header() == 'GEOM':
            with model_header_chunk.read_child() as geom:
                with geom.read_child() as bbox:
                    bounding_box = BoundingBox(
                        rotation=bbox.read_quat(),
                        origin=bbox.read_vec3(),
                        extents=bbox.read_vec3(),
                        sphere_radius=bbox.read_f32()
                    )

                segments = []
                while geom.check_next_header() == 'SEGM':
                    with geom.read_child() as segm:
                        segment = self.parse_segment(segm, self.materials)
                        segments.append(segment)

                cloth = None
                if geom.check_next_header() == 'CLTH':
                    with geom.read_child() as clth:
                        pass

                envelope = None
                if geom.check_next_header() == 'ENVL':
                    with geom.read_child() as envl:
                        pass
            geometry = Geometry(bounding_box, segments, cloth, envelope)
            geometry_list.append(geometry)

        model = Model(
            name=model_name,
            model_type=model_type,
            transform=model_transform,
            geometries=geometry_list
        )
        return model


def parse_msh_file(path):
    parser = MshParser(path)
    parser.parse()
    return parser
