from runtime.win_x64 import atlas_occ


def model() -> list[list[float]]:
    shape = atlas_occ.make_box(100, 50, 25)
    return atlas_occ.get_triangles(shape)
