import os

import numpy as np
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer, Qt
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.util.numpy_support import numpy_to_vtk
import vtk
import psutil


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
            self.memory_timer.stop()  # Stop the timer if an error occurs

    def load_triangles(self, tris: list[list[float]]) -> None:
        """ Loads triangles and displays them in VTK """
        polydata = self.render_mesh(tris)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.2, 0.7, 0.8)

        self.renderer.RemoveAllViewProps()
        self.renderer.AddActor(actor)
        self.renderer.ResetCamera()
        self.vtkWidget.GetRenderWindow().Render()

    @staticmethod
    def render_mesh(tris: list[list[float]]) -> vtk.vtkPolyData:
        """ Render list of 9-float triangles to vtkPolyData """

        tris_np = np.array(tris, dtype=np.float32).reshape(-1, 3, 3)

        # Flatten vertices and deduplicate
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

        # noinspection PyArgumentList
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
