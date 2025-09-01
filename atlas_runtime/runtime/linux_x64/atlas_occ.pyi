"""
Atlas OCC Wrapper — core OCC functionality exposed for intent-driven CAD.
"""
from __future__ import annotations
import collections.abc
import typing
__all__ = ['EXT_API_VERSION', 'TopoDS_Shape', 'bool_cut', 'bool_fuse', 'export_step', 'extrude_shape', 'get_triangles', 'make_box', 'make_compound', 'make_cylinder', 'make_face_from_wire', 'make_wire_circle', 'make_wire_face', 'make_wire_ij2d', 'xform_copy', 'xform_mirror', 'xform_move', 'xform_rotate', 'xform_scale']
class TopoDS_Shape:
    """
    
            A shape object from OpenCascade.
            This class is not created from Python, but returned by modeling functions.
        
    """
def bool_cut(a: TopoDS_Shape, b: TopoDS_Shape) -> TopoDS_Shape:
    """
                Boolean cut (difference): shape A minus shape B.
    
                Parameters:
                    a: First shape (minuend)
                    b: Second shape (subtrahend)
    
                Returns:
                    A TopoDS_Shape result of A - B
    
                Note:
                    Releases the Python GIL during the boolean operation.
    """
def bool_fuse(a: TopoDS_Shape, b: TopoDS_Shape) -> TopoDS_Shape:
    """
                Boolean fuse (union): shape A combined with shape B.
    
                Parameters:
                    a: First shape
                    b: Second shape
    
                Returns:
                    A TopoDS_Shape representing the fused shape
    
                Note:
                    Releases the Python GIL during the boolean operation.
    """
def export_step(shape: TopoDS_Shape, filename: str) -> None:
    """
                Export shape to a STEP file.
    
                Parameters:
                    shape: Shape to export
                    filename: Target .step file path
    
                Returns:
                    None
    
                Note:
                    Releases the Python GIL during the export so other Python threads can run.
    """
def extrude_shape(shape: TopoDS_Shape, dx: typing.SupportsFloat = 0.0, dy: typing.SupportsFloat = 0.0, dz: typing.SupportsFloat = 0.0) -> TopoDS_Shape:
    """
                Extrude a shape in the direction of (dx, dy, dz).
    
                Parameters:
                    shape: A 2D face shape
                    dx: Delta x extrusion vector
                    dy: Delta y extrusion vector
                    dz: Delta z extrusion vector
    
                Returns:
                    A solid shape as extrusion result
    
                Note:
                    Releases the Python GIL during the extrusion.
    """
def get_triangles(shape: TopoDS_Shape) -> list[typing.Annotated[list[float], "FixedSize(9)"]]:
    """
              Extract triangle mesh data from a TopoDS_Shape.
    
              Returns:
                  A list of triangles, each represented as a list of 9 floats (3 vertices x 3 coords).
    
              Note:
                  Releases the Python GIL during meshing/triangulation.
    """
def make_box(x: typing.SupportsFloat, y: typing.SupportsFloat, z: typing.SupportsFloat) -> TopoDS_Shape:
    """
                Create a rectangular box shape.
    
                Parameters:
                    x: Width along X axis
                    y: Depth along Y axis
                    z: Height along Z axis
    
                Returns:
                    A TopoDS_Shape representing the box
    """
def make_compound(shapes: collections.abc.Sequence[TopoDS_Shape]) -> TopoDS_Shape:
    """
                Combine multiple shapes into a single compound object.
    
                Parameters:
                    shapes: List of TopoDS_Shapes
    
                Returns:
                    Compound TopoDS_Shape
    
                Note:
                    Releases the Python GIL while building the compound.
    """
def make_cylinder(radius: typing.SupportsFloat, height: typing.SupportsFloat) -> TopoDS_Shape:
    """
                Create a vertical cylinder along the Z axis.
    
                Parameters:
                    radius: Radius of the cylinder
                    height: Height of the cylinder
    
                Returns:
                    A TopoDS_Shape representing the cylinder
    """
def make_face_from_wire(wire: TopoDS_Shape) -> TopoDS_Shape:
    """
                Convert a closed wire into a planar face.
    
                Parameters:
                    wire: A TopoDS_Shape representing a closed wire
    
                Returns:
                    A TopoDS_Shape representing the face
    """
def make_wire_circle(radius: typing.SupportsFloat, center: collections.abc.Sequence[typing.SupportsFloat], face: bool = False) -> TopoDS_Shape:
    """
                Create a circular wire (or face) in the X-Y plane.
    
                Parameters:
                    radius: Radius of the circle
                    center: List of 3 floats [x, y, z]
                    face: Whether to convert wire into a face
    
                Returns:
                    A TopoDS_Shape as wire or face
    """
def make_wire_face(points: collections.abc.Sequence[collections.abc.Sequence[typing.SupportsFloat]], close: bool = True, face: bool = False) -> TopoDS_Shape:
    """
                Create a wire shape from a list of 3D points. Optionally close it and convert to a face.
    
                Parameters:
                    points: List of [x, y, z] points
                    close: Whether to close the wire
                    face: If true, convert the wire into a face
    
                Returns:
                    A TopoDS_Shape representing a wire or a face
    """
def make_wire_ij2d(segments: collections.abc.Sequence[dict], start: typing.Annotated[collections.abc.Sequence[typing.SupportsFloat], "FixedSize(2)"] = [0.0, 0.0], close: bool = False, plane: str = 'XY') -> TopoDS_Shape:
    """
                Build a 2D wire on a principal plane using CNC-style segments.
    
                segments: list of dicts with keys:
                x, y              -> required end point on plane
                i, j              -> optional center-offset from current point (arc if given)
                cw: bool          -> True = clockwise, False = CCW (default)
    
                start: [u0, v0] on chosen plane (e.g., XY -> [x0, y0])
                close: add final edge back to start if True
                plane: 'XY' (default), 'XZ', or 'YZ'
    
                Flat sketch: no third-axis motion.
    """
def xform_copy(shape: TopoDS_Shape, dx: typing.SupportsFloat = 0.0, dy: typing.SupportsFloat = 0.0, dz: typing.SupportsFloat = 0.0) -> TopoDS_Shape:
    """
                Copy (duplicate) a shape by (dx, dy, dz) by baking the transform.
                This creates a NEW TShape (independent geometry). Heavier than xform_move.
    
                Parameters:
                    shape: Shape to move
                    dx: Offset along X
                    dy: Offset along Y
                    dz: Offset along Z
    
                Returns:
                    Translated as new shape
    """
def xform_mirror(shape: TopoDS_Shape, nx: typing.SupportsFloat = 0.0, ny: typing.SupportsFloat = 0.0, nz: typing.SupportsFloat = 0.0) -> TopoDS_Shape:
    """
            Mirror shape across a plane with normal vector (nx, ny, nz).
    
            Parameters:
                shape: Shape to mirror
                nx: Normal vector defining the mirror plane z
                ny: Normal vector defining the mirror plane y
                nz: Normal vector defining the mirror plane z
    
            Returns:
                Mirrored shape
    """
def xform_move(shape: TopoDS_Shape, dx: typing.SupportsFloat = 0.0, dy: typing.SupportsFloat = 0.0, dz: typing.SupportsFloat = 0.0) -> TopoDS_Shape:
    """
                Translate a shape along X, Y, Z axes.
    
                Parameters:
                    shape: Shape to move
                    dx: Offset along X
                    dy: Offset along Y
                    dz: Offset along Z
    
                Returns:
                    Translated shape
    """
def xform_rotate(shape: TopoDS_Shape, angle_deg: typing.SupportsFloat, ax: typing.SupportsFloat = 0.0, ay: typing.SupportsFloat = 0.0, az: typing.SupportsFloat = 0.0) -> TopoDS_Shape:
    """
            Rotate shape around axis defined by vector (ax, ay, az).
    
            Parameters:
                shape: Shape to rotate
                angle_deg: Rotation angle in degrees
                ax: Axis of rotation (Around x axis)
                ay: Axis of rotation (Around y axis)
                az: Axis of rotation (Around z axis)
    
            Returns:
                Rotated shape
    """
def xform_scale(shape: TopoDS_Shape, sx: typing.SupportsFloat = 0.0, sy: typing.SupportsFloat = 0.0, sz: typing.SupportsFloat = 0.0) -> TopoDS_Shape:
    """
                Scale shape uniformly. (Currently supports only uniform scaling: sx == sy == sz)
    
                Parameters:
                    shape: Shape to scale
                    sx: Scale factor along x axis
                    sy: Scale factor along y axis
                    sz: Scale factor along z axis
    
                Returns:
                    Scaled shape
    """
EXT_API_VERSION: str = '0.2.0'
