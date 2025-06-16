from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, \
    QWidget
from PySide6.QtCore import QTimer, Qt
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk
import psutil
import os
import sys


class VTKQtViewer(QMainWindow):
    def __init__(self, stl_path=None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle('PySide6 VTK Viewer')
        self.setGeometry(100, 100, 800, 600)

        # --- Central Widget Setup ---
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- VTK Widget ---
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.vtkWidget.setMinimumSize(800, 600)
        layout.addWidget(self.vtkWidget)

        self.renderer = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)

        if stl_path:
            self.load_stl(stl_path)

        self.vtkWidget.Initialize()
        self.vtkWidget.Start()

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
            self.vtkWidget.width() - self.memory_label.width() - 18,
            16
        )
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
        """ Always keeps the label top-rigth (with 16px padding) """
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

    def load_stl(self, stl_path) -> None:
        """ Just a temporary file to display while the wrapper is built """
        self.renderer.RemoveAllViewProps()
        reader = vtk.vtkSTLReader()
        reader.SetFileName(stl_path)
        reader.Update()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())  # type: ignore
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.2, 0.7, 0.8)
        self.renderer.AddActor(actor)
        self.renderer.ResetCamera()
        self.vtkWidget.GetRenderWindow().Render()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = VTKQtViewer()
    viewer.show()
    sys.exit(app.exec())
