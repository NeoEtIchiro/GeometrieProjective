from matrices import *
import pygame
import numpy as np
from utils import to_screen, project_perspective

class Face:
    def __init__(self, points, color=(200, 200, 200), position=[0,0,0], angles=[0, 0, 0]):
        self.points = np.array(points, dtype=float)
        self.color = color
        self.angles = list(map(float, angles))
        self.scale = 1
        self.position = np.array(position, dtype=float)

    def apply_transform(self):
        M = HOMOTHETIE(self.scale) @ ROTATION_Y(self.angles[1]) @ ROTATION_X(self.angles[0]) @ ROTATION_Z(self.angles[2])
        pts = M @ self.points.T
        pts = pts.T + self.position
        return pts

    def draw(self, surface, R_view, camera_pos=np.array([0.0, 0.0, 0.0]), d=10):
        pts3d_world = self.apply_transform()
        if pts3d_world.shape[0] < 3:
            return

        pts3d = (R_view @ (pts3d_world - camera_pos).T).T

        # near-plane culling (pas la cause ici, on garde)
        if np.any(pts3d[:, 2] <= 1e-6):
            return

        # back-face culling tolérant (garde les silhouettes)
        v0, v1, v2 = pts3d[0], pts3d[1], pts3d[2]
        n = np.cross(v1 - v0, v2 - v0)  # normale en espace caméra
        if np.linalg.norm(n) < 1e-9:
            return  # face dégénérée
        center = pts3d.mean(axis=0)     # vecteur cam->face (caméra à l’origine)
        eps = 1e-6
        # Si dot(n, center) > eps => face dos caméra -> on cull
        if np.dot(n, center) < -eps:
            return
        # Si l’orientation de tes faces est inversée, remplace '>' par '<'.

        pts2d = project_perspective(pts3d, d=d)
        pygame.draw.polygon(surface, self.color, to_screen(pts2d))