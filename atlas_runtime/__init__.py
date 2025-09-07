from __future__ import annotations
from dataclasses import dataclass, field
from types import ModuleType
from typing import Any, Optional
import os, sys, platform, importlib

__all__ = ['atlas_occ',
           'AtlasPart',
           'AtlasAssembly',
           'AtlasInstance']

_RT = os.getenv('ATLAS_RUNTIME')


def _rt() -> str:
    if _RT: return _RT
    s = platform.system()
    if s == 'Windows': return 'win_x64'
    if s == 'Linux':   return 'linux_x64'
    # if s == 'Darwin':  return 'mac_universal'  # adjust if needed
    raise RuntimeError(f'Unsupported OS: {s}')


_dlldir = os.path.join(os.path.dirname(__file__), 'runtime', _rt())

if _dlldir not in sys.path:
    sys.path.insert(0, _dlldir)

if platform.system() == 'Windows':
    if hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(_dlldir)
    else:
        os.environ['PATH'] = _dlldir + os.pathsep + os.environ.get('PATH', '')
else:
    os.environ['LD_LIBRARY_PATH'] = (
            _dlldir + os.pathsep + os.environ.get('LD_LIBRARY_PATH', ''))

atlas_occ: ModuleType = importlib.import_module('atlas_occ')

TopoDS_Shape = Any


@dataclass(frozen=True)
class AtlasBom:
    part_no: str
    qty: float
    unit: str = 'pcs'
    desc: str = ''
    props: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AtlasPart:
    def_id: str
    shape: TopoDS_Shape
    part_no: str
    desc: str = ''
    material: Optional[str] = None
    drawings: list[str] = field(default_factory=list)
    props: dict[str, Any] = field(default_factory=dict)
    bom_line: Optional[AtlasBom] = None


@dataclass(frozen=False)
class AtlasInstance:
    ref: AtlasPart
    xform: Any = (0.0, 0.0, 0.0)
    qty: int = 1
    children: list['AtlasInstance'] = field(default_factory=list)
    bom_role: str = 'normal'  # normal | phantom | purchased
    overrides: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=False)
class AtlasAssembly:
    root: AtlasInstance
    # Caches for GUI/export
    triangles: Optional[list[list[float]]] = None
    viewer_instances: Optional[list[tuple[str, Any, int]]] = None
    compound: Optional[TopoDS_Shape] = None
    bom_total: Optional[list[AtlasBom]] = None
    dirty: bool = True


from atlas_runtime.asm_utils import (normalize_assembly,
                                     build_compound_and_triangles,
                                     bom_flat, bom_rollup)

__all__ += ['normalize_assembly',
            'build_compound_and_triangles',
            'bom_flat',
            'bom_rollup']
