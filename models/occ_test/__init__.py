from atlas_runtime import load_atlas_occ

PARAMS = [
    {'name': 'width', 'type': float, 'default': 100.0,
     'label': 'Width (mm)', 'unit': 'mm'},
    {'name': 'height', 'type': float, 'default': 50.0,
     'label': 'Height (mm)', 'unit': 'mm'},
    {'name': 'depth', 'type': float, 'default': 25.0,
     'label': 'Depth (mm)', 'unit': 'mm'}
]


def model(**kw) -> list[list[float]]:
    ao = load_atlas_occ()
    w = float(kw.get('width'))
    h = float(kw.get('height'))
    d = float(kw.get('depth'))
    shape = ao.make_box(w, h, d)
    return ao.get_triangles(shape)
