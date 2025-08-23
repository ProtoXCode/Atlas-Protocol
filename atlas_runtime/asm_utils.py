from __future__ import annotations
from typing import Any, Dict, List, Sequence, Tuple
from . import atlas_occ, AtlasPart, AtlasAssembly, AtlasInstance, AtlasBom, \
    TopoDS_Shape


def _identity_xf() -> Tuple[float, float, float]:
    return 0.0, 0.0, 0.0


def _compose(a: Tuple[float, float, float],
             b: Tuple[float, float, float]) -> Tuple[float, float, float]:
    ax, ay, az = a
    bx, by, bz = b
    return ax + bx, ay + by, az + bz


def _apply_xf(shape: TopoDS_Shape, xf: Any) -> TopoDS_Shape:
    if isinstance(xf, (tuple, list)) and len(xf) == 3:
        return atlas_occ.xform_translate(shape, float(xf[0]), float(xf[1]),
                                         float(xf[2]))
    return shape


# ---- Normalization to AtlasAssembly(root=...) ----

def _make_root(children: List[AtlasInstance]) -> AtlasAssembly:
    # Synthetic "root" part (shape=None). def_id/part_no are placeholders.
    root_part = AtlasPart(def_id='_ASM_ROOT', shape=None, part_no='ASM-ROOT')
    root = AtlasInstance(
        ref=root_part, xform=_identity_xf(), qty=1, children=children)
    return AtlasAssembly(root=root, dirty=True)


def normalize_assembly(result: Any) -> AtlasAssembly:
    """
    Accepts:
      - AtlasAssembly
      - List[AtlasPart]
      - List[TopoDS_Shape]
      - None / empty
    Returns AtlasAssembly(root=...) with dirty=True.
    """
    if isinstance(result, AtlasAssembly):
        return result

    if isinstance(result, list):
        if not result:
            return _make_root([])

        first = result[0]
        # List[AtlasPart]
        if hasattr(first, 'shape') and hasattr(first, 'def_id') and hasattr(
                first, 'part_no'):
            children = [AtlasInstance(ref=p, xform=_identity_xf(), qty=1) for p
                        in result]
            return _make_root(children)

        # List[TopoDS_Shape] -> wrap as minimal AtlasPart
        parts: List[AtlasPart] = []
        for i, s in enumerate(result):
            parts.append(AtlasPart(
                def_id=f'_P{i + 1}',
                shape=s,
                part_no=f'P-{i + 1}',
            ))
        children = [AtlasInstance(ref=p, xform=_identity_xf(), qty=1) for p in
                    parts]
        return _make_root(children)

    # Fallback: empty root
    return _make_root([])


# ---- Walk & flatten ----

def walk_instances(inst: AtlasInstance,
                   parent_qty: int = 1,
                   parent_xf: Tuple[float, float, float] = _identity_xf()):
    """DFS yielding (instance, abs_qty, abs_xform)."""
    abs_qty = parent_qty * int(getattr(inst, 'qty', 1))
    # compose only if both are simple tuples; otherwise pass child xform through
    child_xf = inst.xform if inst.xform is not None else _identity_xf()
    abs_xf = _compose(parent_xf, child_xf) if isinstance(parent_xf, (tuple,
                                                                     list)) and isinstance(
        child_xf, (tuple, list)) else child_xf
    yield inst, abs_qty, abs_xf
    for ch in inst.children or []:
        yield from walk_instances(ch, abs_qty, abs_xf)


def collect_shapes(asm: AtlasAssembly) -> List[TopoDS_Shape]:
    """Expand the tree into placed shapes (applying simple (dx,dy,dz) transforms)."""
    shapes: List[TopoDS_Shape] = []
    for node, qty, xf in walk_instances(asm.root):
        shp = getattr(node.ref, 'shape', None)
        if shp is None:
            continue
            # repeat by qty (later: instance-aware viewer/export)
        for _ in range(int(qty)):
            shapes.append(_apply_xf(shp, xf))
    return shapes


# ---- Cache builder ----

def build_compound_and_triangles(asm: AtlasAssembly) -> None:
    """
    Build and cache compound + triangles on the assembly.
    Mutates asm (requires AtlasAssembly NOT frozen).
    """
    if ((not asm.dirty) and asm.compound is not None and
            asm.triangles is not None):
        return

    shapes = collect_shapes(asm)
    if not shapes:
        asm.compound = None
        asm.triangles = []
        asm.dirty = False
        return

    comp = atlas_occ.make_compound(shapes)
    tris = atlas_occ.get_triangles(comp)
    asm.compound = comp
    asm.triangles = tris
    asm.dirty = False


# ---- BOM helpers ----

def bom_flat(asm: AtlasAssembly) -> List[Dict[str, Any]]:
    """
    Basic flat BOM lines with qty rolled down the tree.
    Priority:
      - If part has bom_line -> use that, multiplied by abs qty.
      - Else if leaf (no children) and has part_no -> emit 1*qty.
    """
    lines: List[Dict[str, Any]] = []
    for node, qty, _xf in walk_instances(asm.root):
        ref = node.ref
        # Skip synthetic root
        if ref.part_no == 'ASM-ROOT':
            continue

        # Purchased/explicit line
        if ref.bom_line is not None:
            bl: AtlasBom = ref.bom_line
            lines.append({
                'part_no': bl.part_no, 'qty': float(bl.qty) * float(qty),
                'unit': bl.unit, 'desc': bl.desc, 'props': bl.props
            })
            continue

        if not (node.children or []) and ref.part_no:
            lines.append({
                'part_no': ref.part_no, 'qty': float(qty),
                'unit': 'pcs', 'desc': getattr(ref, 'desc', ''),
                'props': getattr(ref, 'props', {})
            })
    return lines


def bom_rollup(lines: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Group by (part_no, unit) and sum qty."""
    from collections import defaultdict
    b = defaultdict(lambda: {'qty': 0.0, 'unit': '', 'desc': '', 'props': {}})
    for ln in lines:
        key = (ln['part_no'], ln.get('unit', 'pcs'))
        b[key]['qty'] += float(ln.get('qty', 0.0))
        b[key]['unit'] = ln.get('unit', 'pcs') or b[key]['unit']
        b[key]['desc'] = ln.get('desc', '') or b[key]['desc']

    out: List[Dict[str, Any]] = []
    for (pn, unit), v in b.items():
        out.append(
            {'part_no': pn, 'qty': v['qty'], 'unit': unit, 'desc': v['desc']})
    return out
