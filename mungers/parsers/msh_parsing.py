from core.types.material import MaterialData, MaterialAttributes, Material
from core.types.model import SceneInfo, BoundingBox, ModelTransform, CollisionPrimitive, GeometrySegment, Geometry, \
    Model
from mungers.util.BinaryReader import BinaryReader


def parse_scene_info(scene_info_chunk):
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

    scene_info_data = SceneInfo(scene_name, start_frame, end_frame, frame_rate, bounding_box)
    return scene_info_data


def parse_materials_list(materials_list_chunk):
    num_materials = materials_list_chunk.read_u32()
    materials_list = []
    while materials_list_chunk.check_next_header() == 'MATD':
        if len(materials_list) == num_materials:
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
            materials_list.append(material)

    return materials_list


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
                raise ValueError(f'Tri strip #{i} has a START_OF_STRIP bit but is immediately preceded by two others. '
                                 f'This should not happen.')
        strip_buffer.append(index & 0x7FFF)
    if strip_buffer:
        tri_strips.append(strip_buffer)
    return tri_strips


def parse_segment(segment_chunk, materials_list):
    is_shadow_mesh = False
    if segment_chunk.check_next_header() == 'SHDW':
        is_shadow_mesh = True
        pass

    if segment_chunk.check_next_header() == 'MATI':
        with segment_chunk.read_child() as mati:
            material_index = mati.read_u32()

    coordinates = []
    if not is_shadow_mesh:
        with segment_chunk.read_child() as posl:
            num_coordinates = posl.read_u32()
            for _ in range(num_coordinates):
                coordinates.append(posl.read_vec3())

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
    if not is_shadow_mesh:
        with segment_chunk.read_child() as nrml:
            num_normals = nrml.read_u32()
            for _ in range(num_normals):
                normals.append(nrml.read_vec3())

    uvs = []
    if segment_chunk.check_next_header() == 'UV0L':
        with segment_chunk.read_child() as uv0l:
            num_uvs = nrml.read_u32()
            for _ in range(num_uvs):
                uvs.append(nrml.read_vec2())

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
            tri_strips = parse_tri_strips(strp, num_indices)

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


def parse_model(model_header_chunk, materials_list):
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
                shape=swci.read_i32(),
                radius=swci.read_f32(),
                height=swci.read_f32(),
                length=swci.read_f32()
            )
            collision_primitives.append(primitive)

    geometry_list = []
    while model_header_chunk.check_next_header() == 'GEOM':
        with model_header_chunk.read_child() as geom:
            with model_header_chunk.read_child() as bbox:
                bounding_box = BoundingBox(
                    rotation=bbox.read_quat(),
                    origin=bbox.read_vec3(),
                    extents=bbox.read_vec3(),
                    sphere_radius=bbox.read_f32()
                )

            segments = []
            while model_header_chunk.check_next_header() == 'SEGM':
                with model_header_chunk.read_child() as segm:
                    segment = parse_segment(segm, materials_list)
                    segments.append(segment)

            cloth = None
            if model_header_chunk.check_next_header() == 'CLTH':
                with model_header_chunk.read_child() as clth:
                    pass

            envelope = None
            if model_header_chunk.check_next_header() == 'ENVL':
                with model_header_chunk.read_child() as envl:
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


def parse_msh_file(msh_file_path):
    with msh_file_path.open('rb') as f:
        with BinaryReader(f) as file_root:
            with file_root.read_child() as header:
                with header.read_child() as msh2:
                    with msh2.read_child() as sinf:
                        scene_info = parse_scene_info(sinf)
                    if msh2.check_next_header() == 'CAMR':
                        with msh2.read_child() as camr:
                            msh2.skip(camr.size)
                    with msh2.read_child() as matl:
                        materials_list = parse_materials_list(matl)
                    models = []
                    while msh2.check_next_header() == 'MODL':
                        with msh2.read_child() as modl:
                            models.append(parse_model(modl, materials_list))
    return models
