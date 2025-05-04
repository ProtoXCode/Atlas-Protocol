!pip install trimesh
!pip install cadquery
!pip install pythonocc-core
!apt-get update

import trimesh
import cadquery as cq
from dataclasses import dataclass
from cadquery import exporters

LENGTH = 1000
WIDTH = 100
THICKNESS = 10

HOLE_DIAMETER = 20
HOLE_EDGE_DISTANCE = 100

@dataclass
class PartSize:
    length: float
    width: float
    height: float

piece = PartSize(LENGTH, WIDTH, THICKNESS)

hole_positions = [
    (-piece.length / 2 + HOLE_EDGE_DISTANCE, 0),
    (piece.length / 2 - HOLE_EDGE_DISTANCE, 0)]

# Draws the actual part
work_piece = cq.Workplane('XY').box(piece.length, piece.width, piece.height)
work_piece = work_piece.faces('>Z').workplane().pushPoints(hole_positions).hole(HOLE_DIAMETER)

from google.colab import files
cq.exporters.export(work_piece, 'work_piece.step')
files.download('work_piece.step') # Downloads the file

exporters.export(work_piece, 'work_piece.stl')

mesh = trimesh.load('work_piece.stl')
mesh.show()!pip install trimesh
!pip install cadquery
!pip install pythonocc-core
!apt-get update


import trimesh
import cadquery as cq
from dataclasses import dataclass
from cadquery import exporters

LENGTH = 1000
WIDTH = 100
THICKNESS = 10

HOLE_DIAMETER = 20
HOLE_EDGE_DISTANCE = 100

@dataclass
class PartSize:
    length: float
    width: float
    height: float

piece = PartSize(LENGTH, WIDTH, THICKNESS)

hole_positions = [
    (-piece.length / 2 + HOLE_EDGE_DISTANCE, 0),
    (piece.length / 2 - HOLE_EDGE_DISTANCE, 0)
]

# Draws the actual part
work_piece = cq.Workplane('XY').box(piece.length, piece.width, piece.height)
work_piece = work_piece.faces('>Z').workplane().pushPoints(hole_positions).hole(HOLE_DIAMETER)

from google.colab import files
cq.exporters.export(work_piece, 'work_piece.step')
files.download('work_piece.step') # Downloads the file

exporters.export(work_piece, 'work_piece.stl')

mesh = trimesh.load('work_piece.stl')
mesh.show()
