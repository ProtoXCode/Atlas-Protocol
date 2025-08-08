from runtime.win_x64 import atlas_occ

PARAMS = [
    {'name': 'width', 'type': float, 'default': 100.0,
     'label': 'Width (mm)', 'unit': 'mm'},
    {'name': 'height', 'type': float, 'default': 50.0,
     'label': 'Height (mm)', 'unit': 'mm'},
    {'name': 'depth', 'type': float, 'default': 25.0,
     'label': 'Depth (mm)', 'unit': 'mm'},
]

def model(**kw) -> list[list[float]]:
    w = float(kw.get('width'))
    h = float(kw.get('height'))
    d = float(kw.get('depth'))
    shape = atlas_occ.make_box(w, h, d)
    return atlas_occ.get_triangles(shape)
