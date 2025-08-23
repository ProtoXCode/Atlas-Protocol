from atlas_runtime import atlas_occ, AtlasAssembly, AtlasPart, AtlasInstance

# PARAMS are passed to the GUI and turned into editable fields.

PARAMS = [
    {'name': 'width', 'type': float, 'default': 100.0, 'label': 'Width (mm)',
     'unit': 'mm'},
    {'name': 'height', 'type': float, 'default': 50.0, 'label': 'Height (mm)',
     'unit': 'mm'},
    {'name': 'depth', 'type': float, 'default': 25.0, 'label': 'Depth (mm)',
     'unit': 'mm'}]


def assembly(**kw) -> AtlasAssembly:
    """Return a proper AtlasAssembly: root -> [single box instance]."""
    w = float(kw.get('width'))
    h = float(kw.get('height'))
    d = float(kw.get('depth'))

    shape = atlas_occ.make_box(w, h, d)
    size_tag = f'{int(w)}x{int(h)}x{int(d)}'
    part = AtlasPart(
        def_id=f'BOX-{size_tag}',
        shape=shape,
        part_no=f'BOX-{size_tag}',
        desc=f'Box {w}×{h}×{d} mm',
        material=None,
        drawings=[],
        props={},
        bom_line=None)

    inst = AtlasInstance(ref=part, xform=(0.0, 0.0, 0.0), qty=1)

    root_part = AtlasPart(def_id='_ROOT_SINGLE_BOX', shape=None,
                          part_no='ASM-BOX',
                          desc=f'Single box {size_tag}')
    root = AtlasInstance(ref=root_part, xform=(0.0, 0.0, 0.0), qty=1,
                         children=[inst])

    return AtlasAssembly(root=root, dirty=True)
