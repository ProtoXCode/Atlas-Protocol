from __future__ import annotations
import time, traceback
import logging
import threading
import numpy as np

from PySide6.QtCore import QObject, Signal, QRunnable

from atlas_runtime.asm_utils import normalize_assembly, \
    build_compound_and_triangles


class WorkerSignals(QObject):
    result = Signal(object, dict)  # (processed_data, stats)
    error = Signal(str)
    finished = Signal()
    progress = Signal(str)


class ModelRunnable(QRunnable):
    def __init__(self, fn, kwargs: dict) -> None:
        super().__init__()
        self.fn = fn
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.setAutoDelete(True)

    @staticmethod
    def _count_solid_instances(inst) -> int:
        total = 0
        stack = [(inst, 1)]
        while stack:
            node, parent_qty = stack.pop()
            qty = parent_qty * int(getattr(node, 'qty', 1))
            if getattr(getattr(node, 'ref', None), 'shape', None) is not None:
                total += qty
            for ch in getattr(node, 'children', []) or []:
                stack.append((ch, qty))
        return total

    def run(self) -> None:
        thread_id = threading.get_ident()
        logging.info(
            f"[worker] Starting full processing on thread {thread_id}")

        try:
            t_all = time.perf_counter()

            # Step 1: Model execution
            self.signals.progress.emit("Executing model...")
            t0 = time.perf_counter()
            result = self.fn(**self.kwargs)
            t_model = time.perf_counter() - t0

            # Step 2: Normalize
            self.signals.progress.emit("Normalizing assembly...")
            t1 = time.perf_counter()
            asm = normalize_assembly(result)
            t_norm = time.perf_counter() - t1

            # Step 3: Build triangles (the expensive part)
            self.signals.progress.emit("Building geometry...")
            t2 = time.perf_counter()
            build_compound_and_triangles(asm)
            t_cache = time.perf_counter() - t2

            if not asm.triangles:
                raise TypeError('Model produced no triangles')

            # Step 4: Pre-process triangles for VTK (reduce main thread work)
            self.signals.progress.emit("Optimizing triangles for display...")
            t3 = time.perf_counter()

            # Pre-process triangles to reduce VTK work
            processed_triangles = self._optimize_triangles_for_vtk(
                asm.triangles)

            t_vtk_prep = time.perf_counter() - t3

            # Step 5: Count instances
            self.signals.progress.emit("Counting instances...")
            try:
                t_inst = self._count_solid_instances(asm.root)
            except Exception as e:
                logging.exception(f'[worker] instance count failed: {e}')
                t_inst = 0

            # Package everything for main thread
            processed_data = {
                'assembly': asm,
                'triangles': processed_triangles,
                'original_triangles': len(asm.triangles)
            }

            stats = {
                't_model': t_model,
                't_norm': t_norm,
                't_cache': t_cache,
                't_vtk_prep': t_vtk_prep,
                't_inst': t_inst,
                't_total': time.perf_counter() - t_all,
                'tris': len(asm.triangles),
            }

            logging.info(
                f"[worker] Full processing completed on thread {thread_id}")
            logging.info(
                f"[worker] Times: model={t_model:.3f}s norm={t_norm:.3f}s cache={t_cache:.3f}s prep={t_vtk_prep:.3f}s")

            self.signals.result.emit(processed_data, stats)

        except Exception as e:
            error_msg = traceback.format_exc()
            logging.error(
                f'[worker] Exception on thread {thread_id}: {error_msg} - {e}')
            self.signals.error.emit(error_msg)
        finally:
            self.signals.finished.emit()

    @staticmethod
    def _optimize_triangles_for_vtk(triangles):
        """Pre-process triangles to reduce VTK processing time"""

        if len(triangles) < 5000:
            return triangles  # Small models don't need optimization

        logging.info(f"[worker] Optimizing {len(triangles):,} triangles")

        # Convert to numpy early (in worker thread)
        tris_np = np.array(triangles, dtype=np.float32).reshape(-1, 3, 3)

        # Pre-deduplicate points (the expensive part of VTK processing)
        points = []
        faces = []
        point_id_map = {}
        next_id = 0

        for i, tri in enumerate(tris_np):
            if i > 0 and i % 20000 == 0:
                logging.info(
                    f"[worker] Optimized {i:,}/{len(tris_np):,} triangles")

            face_ids = []
            for vert in tri:
                key = tuple(vert.round(6))  # Round to reduce duplicates
                if key not in point_id_map:
                    point_id_map[key] = next_id
                    points.append(vert)
                    next_id += 1
                face_ids.append(point_id_map[key])
            faces.append(face_ids)

        faces_np = np.asarray(faces, dtype=np.int64)

        n_tris = faces_np.shape[0]
        connectivity = faces_np.reshape(-1)
        offsets = np.arange(0, (n_tris + 1) * 3, 3, dtype=np.int64)

        # Return pre-processed data
        return {
            'points': np.asarray(points, dtype=np.float32),
            'faces': faces_np,
            'connectivity': connectivity,
            'offsets': offsets,
            'original_count': len(triangles),
            'optimized_points': len(points),
        }


class ExportSignals(QObject):
    finished = Signal(float, str)  # dt, out_path
    error = Signal(str)
    progress = Signal(str)


class ExportWorker(QRunnable):
    def __init__(self, atlas_occ, compound, path: str) -> None:
        super().__init__()
        self.atlas_occ = atlas_occ
        self.compound = compound
        self.path = path
        self.signals = ExportSignals()
        self.setAutoDelete(True)

    def run(self) -> None:
        thread_id = threading.get_ident()
        logging.info(f'[worker] Starting export on thread {thread_id}')

        try:
            self.signals.progress.emit('Exporting STEP file...')
            t0 = time.perf_counter()

            self.atlas_occ.export_step(self.compound, self.path)

            dt = time.perf_counter() - t0
            logging.info(f'[worker] Export completed in {dt:.3f}s '
                         f'on thread {thread_id}')
            self.signals.finished.emit(dt, self.path)

        except Exception as e:
            error_msg = traceback.format_exc()
            logging.error(
                f'[export] Exception on thread {thread_id}: {error_msg} ({e})')
            self.signals.error.emit(str(error_msg))
