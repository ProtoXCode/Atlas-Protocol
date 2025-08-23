from atlas_runtime import atlas_occ

# PARAMS are passed onto the GUI and is turned into editable fields.
# The assembly simply packs up the components and returns it to GUI.


PARAMS = [
    {'name': 'width', 'type': float, 'default': 100.0,
     'label': 'Width (mm)', 'unit': 'mm'},
    {'name': 'height', 'type': float, 'default': 50.0,
     'label': 'Height (mm)', 'unit': 'mm'},
    {'name': 'depth', 'type': float, 'default': 25.0,
     'label': 'Depth (mm)', 'unit': 'mm'}
]


def make_box(x: float, y: float, z: float):
    """ This function makes a single box shape. """
    shape = atlas_occ.make_box(x, y, z)
    return shape


def assembly(**kw) -> list[list[float]]:
    """ This is the complete assembly of the parts. """
    w = float(kw.get('width'))
    h = float(kw.get('height'))
    d = float(kw.get('depth'))
    shape = make_box(w, h, d)
    shapes = [shape]
    return shapes
