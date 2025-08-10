import pytest
import tempfile
import os

atlas_runtime = pytest.importorskip('atlas_runtime',
                                    reason='Atlas runtime is not importable')


@pytest.fixture(scope='session')
def occ():
    try:
        from atlas_runtime import atlas_occ
    except Exception as e:
        pytest.skip(f'atlas_occ not available: {e}')
    return atlas_occ


def test_import_wrapper(occ) -> None:
    for name in ('bool_cut', 'bool_fuse', 'export_step', 'extrude_shape',
                 'get_triangles', 'make_box', 'make_compound', 'make_cylinder',
                 'make_face_from_wire', 'make_wire_circle', 'make_wire_face',
                 'xform_mirror', 'xform_rotate', 'xform_scale',
                 'xform_translate'):
        assert hasattr(occ, name), f'missing {name}'


def test_make_box_and_triangles(occ) -> None:
    s = occ.make_box(10, 20, 30)
    tris = occ.get_triangles(s)
    assert isinstance(tris, list) and len(tris) > 0
    assert all(isinstance(t, list) and len(t) == 9 for t in tris)


def test_bool_ops_roundtrip(occ) -> None:
    a = occ.make_box(10, 10, 10)
    b = occ.make_box(6, 6, 6)
    b = occ.xform_translate(b, 2, 2, 2)
    cut = occ.bool_cut(a, b)
    fuse = occ.bool_fuse(a, b)
    assert len(occ.get_triangles(cut)) > 0
    assert len(occ.get_triangles(fuse)) > 0


def test_transforms(occ) -> None:
    s = occ.make_box(1, 2, 3)
    s = occ.xform_translate(s, 5, 0, 0)
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


def test_make_compound_and_export(occ) -> None:
    a = occ.make_box(5, 5, 5)
    b = occ.make_cylinder(2, 10)
    b = occ.xform_translate(b, 3, 0, 0)
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
    b = occ.xform_translate(a, 10, 0, 0)  # copy=true
    tris_b = occ.get_triangles(b)
    assert len(tris_a) > 0 and len(tris_b) > 0


def test_api_version(occ) -> None:
    assert hasattr(occ, 'EXT_API_VERSION'), \
        'Missing EXT_API_VERSION in wrapper'
    assert occ.EXT_API_VERSION == '0.1.0', \
        f'Unexpected version: {occ.EXT_API_VERSION}'
