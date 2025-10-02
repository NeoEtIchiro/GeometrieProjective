from render3D.face import Face
import numpy as np

from render3D.consts import *

class Shape:
    def __init__(self, faces, position=[0,0,0], angles=[0,0,0]):
        self.faces = faces
        self.position = np.array(position, dtype=float)  # <--- use float dtype
        self.angles = list(map(float, angles))
        self.scale = 1
            
class Cube(Shape):
    def __init__(self, scale=1, position=[0,0,0], angles=[0,0,0]):
        half = scale / 2
        faces = [
            # Front face
            Face([
                [half, half, half],
                [half, -half, half],
                [-half, -half, half],
                [-half,  half, half]
            ], color=RED, angles=[0, 0, 0], position=[0, 0, 0]),

            # Back face
            Face([
                [half, half, -half],
                [-half, half, -half],
                [-half, -half, -half],
                [half, -half, -half]
            ], color=ORANGE, angles=[0, 0, 0], position=[0, 0, 0]),

            # Right face
            Face([
                [half, half, half],
                [half, half, -half],
                [half, -half,  -half],
                [half,  -half,  half]
            ], color=WHITE, angles=[0, 0, 0], position=[0, 0, 0]),

            # Left face
            Face([
                [-half, half, -half],
                [-half, half, half],
                [-half, -half, half],
                [-half, -half, -half]
            ], color=YELLOW, angles=[0, 0, 0], position=[0, 0, 0]),

            # Top face
            Face([
                [-half, half, -half],
                [half, half, -half],
                [half, half, half],
                [-half, half, half]
            ], color=GREEN, angles=[0, 0, 0], position=[0, 0, 0]),

            # Bottom face
            Face([
                [half, -half, half],
                [half, -half, -half],
                [-half, -half, -half],
                [-half, -half, half]
            ], color=BLUE, angles=[0, 0, 0], position=[0, 0, 0])
        ]
        super().__init__(faces=faces, position=position, angles=angles)