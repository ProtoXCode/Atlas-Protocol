import psutil
import logging
import time
import os
import numpy as np

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QApplication
from PySide6.QtCore import QTimer, Qt
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray
import vtk


class VTKQtViewer(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- VTK Widget ---
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.vtkWidget.setMinimumSize(800, 600)
        layout.addWidget(self.vtkWidget)

        self.renderer = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)

        self.vtkWidget.Initialize()

        # --- Memory Overlay ---
        self.memory_label = QLabel('RAM: --- MB', self.vtkWidget)
        self.memory_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.memory_label.setStyleSheet("""
            background: rgba(30,30,30,190);
            color: #00ffc8;
            font-size: 13px;
            border-radius: 8px;
            padding: 4px 12px;
        """)
        self.memory_label.setFixedWidth(180)
        self.memory_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.memory_label.move(
            self.vtkWidget.width() - self.memory_label.width() - 18, 16)
        self.memory_label.raise_()

        # --- Respond to resizing (keep overlay in top-right) ---
        self.vtkWidget.resizeEvent = self._on_viewer_resize

        # --- QTimer for updates ---
        self.memory_timer = QTimer(self)
        self.memory_timer.setInterval(1000)
        self.memory_timer.timeout.connect(self.update_memory_display)
        self.memory_timer.start()
        self.update_memory_display()

    def _on_viewer_resize(self, event) -> None:
        """ Always keeps the label top-right (with 16px padding) """
        self.memory_label.move(
            self.vtkWidget.width() - self.memory_label.width() - 18, 16)
        # Call the original VTK widget resizeEvent (so VTK still gets notified!)
        QVTKRenderWindowInteractor.resizeEvent(self.vtkWidget, event)

    def update_memory_display(self) -> None:
        """ Fetches and displays the current process memory usage """
        try:
            process = psutil.Process(os.getpid())
            mem_info = process.memory_info()
            # Convert bytes to MB for display
            rss_mb = mem_info.rss / (1024 ** 2)
            vms_mb = mem_info.vms / (1024 ** 2)
            self.memory_label.setText(
                f'RAM: {rss_mb:.2f} MB\nVMS: {vms_mb:.2f} MB')
        except Exception as e:
            self.memory_label.setText(f'Memory: Error ({e})')
            self.memory_timer.stop()

    def load_triangles_optimized(self, processed_data: dict) -> None:
        logging.info(
            f'[vtk] Loading optimized data: {processed_data['optimized_points']} points, '
            f'{processed_data['original_count']} triangles'
        )
        total_start = time.perf_counter()

        try:
            points_np = np.ascontiguousarray(
                processed_data['points'])  # (N, 3) float32 OK

            # ---- robust vtkIdType handling ----
            id_n_bytes = vtk.vtkIdTypeArray().GetDataTypeSize()  # 4 or 8
            id_dtype = np.int64 if id_n_bytes == 8 else np.int32

            offsets_np = np.ascontiguousarray(
                processed_data['offsets'].astype(id_dtype, copy=False)
            )
            conn_np = np.ascontiguousarray(
                processed_data['connectivity'].astype(id_dtype, copy=False)
            )

            vtk_points = vtk.vtkPoints()
            vtk_points.SetData(
                numpy_to_vtk(points_np, deep=False))  # geometry floats

            vtk_cells = vtk.vtkCellArray()

            vtk_offsets = numpy_to_vtkIdTypeArray(offsets_np, deep=True)
            vtk_conn = numpy_to_vtkIdTypeArray(conn_np, deep=True)
            vtk_cells.SetData(vtk_offsets, vtk_conn)

            polydata = vtk.vtkPolyData()
            polydata.SetPoints(vtk_points)
            polydata.SetPolys(vtk_cells)

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputData(polydata)

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(0.2, 0.7, 0.8)

            self.renderer.RemoveAllViewProps()
            self.renderer.AddActor(actor)
            self.renderer.ResetCamera()
            self.vtkWidget.GetRenderWindow().Render()

            logging.info(
                f'[vtk] Total optimized load time: {time.perf_counter() - total_start:.3f}s')

        except Exception as e:
            logging.exception(f'[vtk] Error in load_triangles_optimized: {e}')
            raise

    def load_triangles(self, tris: list[list[float]]) -> None:
        """ Legacy method for compatibility """
        if isinstance(tris, dict):
            # New optimized format
            self.load_triangles_optimized(tris)
        else:
            # Legacy format - process normally but with responsiveness
            self._load_triangles_responsive(tris)

    def _load_triangles_responsive(self, tris: list[list[float]]) -> None:
        """ Load triangles with GUI responsiveness """
        logging.info(f'[vtk] Loading {len(tris)} triangles (legacy mode)')

        total_start = time.perf_counter()

        # Process events before starting
        QApplication.processEvents()

        # For large triangle counts, process in chunks
        if len(tris) > 50000:
            polydata = self._render_mesh_chunked(tris)
        else:
            polydata = self.render_mesh(tris)

        # Create pipeline
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.2, 0.7, 0.8)

        self.renderer.RemoveAllViewProps()
        self.renderer.AddActor(actor)
        self.renderer.ResetCamera()
        self.vtkWidget.GetRenderWindow().Render()

        total_time = time.perf_counter() - total_start
        logging.info(f'[vtk] Legacy load time: {total_time:.3f}s')

    @staticmethod
    def _render_mesh_chunked(tris: list[list[float]]) -> vtk.vtkPolyData:
        """ Render mesh with periodic GUI updates """
        logging.info(f'[vtk] Chunked processing of {len(tris)} triangles')

        tris_np = np.array(tris, dtype=np.float32).reshape(-1, 3, 3)

        points = []
        faces = []
        point_id_map = {}
        next_id = 0

        chunk_size = 10000
        for i in range(0, len(tris_np), chunk_size):
            chunk = tris_np[i:i + chunk_size]

            for tri in chunk:
                face_ids = []
                for vert in tri:
                    key = tuple(vert)
                    if key not in point_id_map:
                        point_id_map[key] = next_id
                        points.append(vert)
                        next_id += 1
                    face_ids.append(point_id_map[key])
                faces.append(face_ids)

            # Process events after each chunk
            if i > 0:
                logging.info(
                    f'[vtk] Processed {i + len(chunk):,}/{len(tris_np):,} triangles')
                QApplication.processEvents()

        # Create VTK structures
        points_np = np.array(points, dtype=np.float32)
        faces_np = np.array(faces, dtype=np.int64)

        vtk_points = vtk.vtkPoints()
        vtk_points.SetData(numpy_to_vtk(points_np))

        vtk_cells = vtk.vtkCellArray()
        for f in faces_np:
            id_list = vtk.vtkIdList()
            for pid in f:
                id_list.InsertNextId(int(pid))
            vtk_cells.InsertNextCell(id_list)

        polydata = vtk.vtkPolyData()
        polydata.SetPoints(vtk_points)
        polydata.SetPolys(vtk_cells)

        return polydata

    @staticmethod
    def render_mesh(tris: list[list[float]]) -> vtk.vtkPolyData:
        """Original render_mesh method for small models"""
        tris_np = np.array(tris, dtype=np.float32).reshape(-1, 3, 3)

        points = []
        faces = []
        point_id_map = {}
        next_id = 0

        for tri in tris_np:
            face_ids = []
            for vert in tri:
                key = tuple(vert)
                if key not in point_id_map:
                    point_id_map[key] = next_id
                    points.append(vert)
                    next_id += 1
                face_ids.append(point_id_map[key])
            faces.append(face_ids)

        points_np = np.array(points, dtype=np.float32)
        faces_np = np.array(faces, dtype=np.int64)

        vtk_points = vtk.vtkPoints()
        vtk_points.SetData(numpy_to_vtk(points_np))

        vtk_cells = vtk.vtkCellArray()
        for f in faces_np:
            id_list = vtk.vtkIdList()
            for pid in f:
                id_list.InsertNextId(int(pid))
            vtk_cells.InsertNextCell(id_list)

        polydata = vtk.vtkPolyData()
        polydata.SetPoints(vtk_points)
        polydata.SetPolys(vtk_cells)

        return polydata
