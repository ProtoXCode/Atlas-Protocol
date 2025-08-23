# Atlas Protocol blueprint — Grid of Boxes
# (drop-in replacement; adds count + spacing controls)

from atlas_runtime import atlas_occ

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


def make_box(x: float, y: float, z: float):
    """Make a single box shape."""
    return atlas_occ.make_box(x, y, z)


def grid(w: float, h: float, d: float,
         nx: int, ny: int, nz: int,
         s: float) -> list:
    """
    Make a grid of boxes.
    s = spacing factor (1.0 -> packed; >1 adds gap)
    """
    shapes = []

    # step distances between box origins
    step_x = w * s
    step_y = h * s
    step_z = d * s

    # build one base box to reuse (faster than remaking each time)
    base = make_box(w, h, d)

    for iz in range(nz):
        z = iz * step_z
        for iy in range(ny):
            y = iy * step_y
            for ix in range(nx):
                x = ix * step_x
                inst = atlas_occ.xform_translate(base, x, y, z)
                shapes.append(inst)

    return shapes


def assembly(**kw) -> list:
    """Complete assembly of the grid."""
    w = float(kw.get('width'))
    h = float(kw.get('height'))
    d = float(kw.get('depth'))

    nx = int(kw.get('count_x'))
    ny = int(kw.get('count_y'))
    nz = int(kw.get('count_z'))
    s = float(kw.get('spacing_factor'))

    return grid(w, h, d, nx, ny, nz, s)
