from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from atlas_runtime.asm_utils import normalize_assembly, \
    build_compound_and_triangles


class ModelWorker(QObject):
    finished = Signal(object, dict)
    error = Signal(str)

    def __init__(self, fn, kwargs: dict) -> None:
        super().__init__()
        self.fn = fn
        self.kwargs = kwargs

    @Slot()
    def run(self) -> None:
        import time
        try:
            t_all = time.perf_counter()

            t0 = time.perf_counter()
            result = self.fn(**self.kwargs)
            t_model = time.perf_counter() - t0

            t1 = time.perf_counter()
            asm = normalize_assembly(result)
            t_norm = time.perf_counter() - t1

            t2 = time.perf_counter()
            build_compound_and_triangles(asm)
            t_cache = time.perf_counter() - t2

            stats = {
                't_model': t_model, 't_norm': t_norm, 't_cache': t_cache,
                't_total': time.perf_counter() - t_all,
                'tris': len(asm.triangles or [])}

            self.finished.emit(asm, stats)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))


class ExportWorker(QObject):
    finished = Signal(float, str)
    error = Signal(str)

    def __init__(self, atlas_occ, compound, path: str) -> None:
        super().__init__()
        self.atlas_occ = atlas_occ
        self.compound = compound
        self.path = path

    @Slot()
    def run(self) -> None:
        import time
        try:
            t0 = time.perf_counter()
            self.atlas_occ.export_step(self.compound, self.path)
            dt = time.perf_counter() - t0
            self.finished.emit(dt, self.path)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))
