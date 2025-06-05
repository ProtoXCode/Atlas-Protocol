import tkinter as tk
import vtk
from vtkmodules.tk.vtkTkRenderWindowInteractor import (
    vtkTkRenderWindowInteractor)
from vtkmodules.vtkIOGeometry import vtkSTLReader
from vtkmodules.vtkRenderingCore import (
    vtkRenderer, vtkPolyDataMapper, vtkActor)


class VTKViewer(tk.Frame):
    """ Embeddable VTK 3D viewer for STL files. *For now* """

    def __init__(self, parent, width=800, height=600, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.width = width
        self.height = height

        self.vtk_widget = vtkTkRenderWindowInteractor(
            self, width=self.width, height=self.height)
        self.vtk_widget.pack(fill='both', expand=True)

        self.renderer = vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.vtk_widget.Initialize()
        self.vtk_widget.Start()

    def load_stl(self, stl_path, color=(0.3, 0.6, 0.9)) -> None:
        """ Load and render an STL file. """
        self.renderer.RemoveAllViewProps()

        reader = vtkSTLReader()
        reader.SetFileName(stl_path)
        reader.Update()

        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*color)

        self.renderer.AddActor(actor)
        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()
