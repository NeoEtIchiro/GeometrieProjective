from render3D.face import Face
import numpy as np

from render3D.consts import *
from render3D.matrices import *

class Shape:
    def __init__(self, faces, position=[0,0,0], rotation_matrix=None, scale=1):
        self.faces = faces
        self.position = np.array(position, dtype=float)
        if rotation_matrix is None:
            self.rotation_matrix = np.eye(3)
        else:
            self.rotation_matrix = np.array(rotation_matrix, dtype=float)
        self.scale = scale
            
    def get_transform_matrix(self):
            return HOMOTHETIE(self.scale) @ self.rotation_matrix

    def draw(self, surface, R_view, camera_pos, d=10):
        M = self.get_transform_matrix()
        for face in self.faces:
            face.draw(surface, R_view, camera_pos, d, M, self.position)

class Cube(Shape):
    def __init__(self, scale=1, position=[0,0,0], rotation_matrix=None):
        half = scale / 2
        faces = [
            Face([
                [half, half, half],
                [half, -half, half],
                [-half, -half, half],
                [-half,  half, half]
            ], color=RED),
            Face([
                [half, half, -half],
                [-half, half, -half],
                [-half, -half, -half],
                [half, -half, -half]
            ], color=ORANGE),
            Face([
                [half, half, half],
                [half, half, -half],
                [half, -half,  -half],
                [half,  -half,  half]
            ], color=WHITE),
            Face([
                [-half, half, -half],
                [-half, half, half],
                [-half, -half, half],
                [-half, -half, -half]
            ], color=YELLOW),
            Face([
                [-half, half, -half],
                [half, half, -half],
                [half, half, half],
                [-half, half, half]
            ], color=GREEN),
            Face([
                [half, -half, half],
                [half, -half, -half],
                [-half, -half, -half],
                [-half, -half, half]
            ], color=BLUE)
        ]
        super().__init__(faces=faces, position=position, rotation_matrix=rotation_matrix, scale=scale)