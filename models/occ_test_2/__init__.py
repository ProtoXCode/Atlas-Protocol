from atlas_runtime import atlas_occ, AtlasAssembly, AtlasPart, AtlasInstance

PARAMS = [
    {'name': 'width', 'type': float, 'default': 100.0, 'label': 'Width (mm)',
     'unit': 'mm'},
    {'name': 'height', 'type': float, 'default': 100.0, 'label': 'Height (mm)',
     'unit': 'mm'},
    {'name': 'depth', 'type': float, 'default': 100.0, 'label': 'Depth (mm)',
     'unit': 'mm'},

    # grid controls
    {'name': 'count_x', 'type': int, 'default': 3, 'label': 'Count X'},
    {'name': 'count_y', 'type': int, 'default': 2, 'label': 'Count Y'},
    {'name': 'count_z', 'type': int, 'default': 2, 'label': 'Count Z'},

    # spacing as a multiplier of size (1.0 = touching, 1.1 = 10% gap)
    {'name': 'spacing_factor', 'type': float, 'default': 1.10,
     'label': 'Spacing (× size)'},
]


def assembly(**kw) -> AtlasAssembly:
    w = float(kw.get('width'))
    h = float(kw.get('height'))
    d = float(kw.get('depth'))
    nx = int(kw.get('count_x'))
    ny = int(kw.get('count_y'))
    nz = int(kw.get('count_z'))
    s = float(kw.get('spacing_factor'))

    base_shape = atlas_occ.make_box(w, h, d)
    size_tag = f"{int(w)}x{int(h)}x{int(d)}"
    part_def = AtlasPart(
        def_id=f"BOX-{size_tag}",
        shape=base_shape,
        part_no=f"BOX-{size_tag}",
        desc=f"Box {w}×{h}×{d} mm",
        material=None,  # fill later
        drawings=[],  # fill later
        props={},  # free-form
        bom_line=None,  # leaf parts will use part_no fallback
    )

    step_x, step_y, step_z = w * s, h * s, d * s
    children: list[AtlasInstance] = []
    for iz in range(nz):
        z = iz * step_z
        for iy in range(ny):
            y = iy * step_y
            for ix in range(nx):
                x = ix * step_x

                children.append(AtlasInstance(
                    ref=part_def, xform=(x, y, z), qty=1))

    root_part = AtlasPart(
        def_id="_GRID_ROOT", shape=None, part_no="ASM-GRID",
        desc=f"Grid {nx}×{ny}×{nz} of {size_tag}"
    )
    root = AtlasInstance(
        ref=root_part, xform=(0.0, 0.0, 0.0), qty=1, children=children)

    return AtlasAssembly(root=root, dirty=True)
