from PySide6.QtWidgets import QWidget, QVBoxLayout
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk


class VTKQtViewer(QWidget):
    def __init__(self, stl_path=None, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        layout.addWidget(self.vtkWidget)
        self.renderer = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
        if stl_path:
            self.load_stl(stl_path)
        self.vtkWidget.Initialize()
        self.vtkWidget.Start()

    def load_stl(self, stl_path) -> None:
        self.renderer.RemoveAllViewProps()
        reader = vtk.vtkSTLReader()
        reader.SetFileName(stl_path)
        reader.Update()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.2, 0.7, 0.8)
        self.renderer.AddActor(actor)
        self.renderer.ResetCamera()
        self.vtkWidget.GetRenderWindow().Render()
