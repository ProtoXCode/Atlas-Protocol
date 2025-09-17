import pytest
import tempfile
import os
import math

atlas_runtime = pytest.importorskip('atlas_runtime',
                                    reason='Atlas runtime is not importable')

WRAPPER_API_VERSION = '0.2.1'  # Update as new versions are released


@pytest.fixture(scope='session')
def occ():
    try:
        from atlas_runtime import atlas_occ
    except Exception as e:
        pytest.skip(f'atlas_occ not available: {e}')

    # noinspection PyUnboundLocalVariable
    return atlas_occ


def test_import_wrapper(occ) -> None:
    for name in ('EXT_API_VERSION', 'TopoDS_Shape', 'bool_cut', 'bool_fuse',
                 'export_step', 'export_stl', 'extrude_shape', 'get_triangles',
                 'make_box', 'make_compound', 'make_cone', 'make_cylinder',
                 'make_face_from_wire', 'make_sphere', 'make_torus',
                 'make_wire_circle', 'make_wire_face', 'make_wire_ij2d',
                 'shape_volume', 'xform_copy', 'xform_mirror', 'xform_move',
                 'xform_rotate', 'xform_scale'):
        assert hasattr(occ, name), f'missing {name}'


def test_api_version(occ) -> None:
    assert hasattr(occ, 'EXT_API_VERSION'), \
        'Missing EXT_API_VERSION in wrapper'
    assert occ.EXT_API_VERSION == WRAPPER_API_VERSION, \
        f'Unexpected version: {occ.EXT_API_VERSION}'


def test_make_box_and_triangles(occ) -> None:
    s = occ.make_box(10, 20, 30)
    tris = occ.get_triangles(s)
    assert isinstance(tris, list) and len(tris) > 0
    assert all(isinstance(t, list) and len(t) == 9 for t in tris)


def test_bool_ops_roundtrip(occ) -> None:
    a = occ.make_box(10, 10, 10)
    b = occ.make_box(6, 6, 6)
    b = occ.xform_move(b, 2, 2, 2)
    cut = occ.bool_cut(a, b)
    fuse = occ.bool_fuse(a, b)
    assert len(occ.get_triangles(cut)) > 0
    assert len(occ.get_triangles(fuse)) > 0


def test_transforms(occ) -> None:
    s = occ.make_box(1, 2, 3)
    s = occ.xform_move(s, 5, 0, 0)
    s = occ.xform_copy(s, 10, 0, 0)
    s = occ.xform_rotate(s, 45, 0, 0, 1)
    s = occ.xform_scale(s, 2, 2, 2)
    s = occ.xform_mirror(s, 1, 0, 0)
    assert len(occ.get_triangles(s)) > 0


def test_step_export_nonempty(occ) -> None:
    s = occ.make_box(10, 10, 10)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, 'cube.step')
        occ.export_step(s, path)
        assert os.path.exists(path)
        with open(path, 'rb') as f:
            head = f.read(32)
        assert b'ISO-10303-21' in head


def test_stl_export_nonempty(occ) -> None:
    s = occ.make_sphere(10)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, 'sphere.stl')
        ok = occ.export_stl(s, path)
        assert ok is True
        assert os.path.exists(path)
        with open(path, 'rb') as f:
            data = f.read(100)
        assert len(data) >= 84
        tri_count = int.from_bytes(data[80:84], byteorder='little')
        assert tri_count > 0


def test_make_compound_and_export(occ) -> None:
    a = occ.make_box(5, 5, 5)
    b = occ.make_cylinder(2, 10)
    b = occ.xform_move(b, 3, 0, 0)
    c = occ.make_compound([a, b])
    assert len(occ.get_triangles(c)) > 0


def test_wire_circle_face_flag(occ) -> None:
    w = occ.make_wire_circle(radius=5.0, center=[0, 0, 0], face=False)
    f = occ.make_wire_circle(radius=5.0, center=[0, 0, 0], face=True)
    assert len(occ.get_triangles(f)) >= len(occ.get_triangles(w))


def test_compound_empty_raises(occ) -> None:
    with pytest.raises(Exception):
        occ.make_compound([])


def test_compound_identity(occ) -> None:
    a = occ.make_box(10, 10, 10)
    c = occ.make_compound([a])
    assert len(occ.get_triangles(c)) > 0


def test_translate_does_not_mutate_input(occ) -> None:
    a = occ.make_box(1, 2, 3)
    tris_a = occ.get_triangles(a)
    b = occ.xform_move(a, 10, 0, 0)
    tris_b = occ.get_triangles(b)
    assert len(tris_a) > 0 and len(tris_b) > 0


def test_volume_box(occ) -> None:
    s = occ.make_box(10, 20, 30)
    v = occ.shape_volume(s)
    assert abs(v - 6000) < 1e-6  # Volume = 10 * 20 * 30 = 6000


def test_volume_cylinder(occ) -> None:
    s = occ.make_cylinder(5, 10)
    v = occ.shape_volume(s)
    expected = math.pi * 25 * 10  # Volume = π * r^2 * h
    assert abs(v - expected) / expected < 1e-6


def test_make_torus(occ) -> None:
    s = occ.make_torus(5, 10)
    assert s is not None
    tris = occ.get_triangles(s)
    assert isinstance(tris, list) and len(tris) > 0
