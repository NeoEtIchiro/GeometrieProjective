import pygame
import numpy as np
from render3D.utils import to_screen, project_perspective

class Face:
    def __init__(self, points, color=(200, 200, 200)):
        self.points = np.array(points, dtype=float)
        self.color = color

    def get_transformed_points(self, M, position):
        pts = (M @ self.points.T).T + position
        return pts

    def draw(self, surface, R_view, camera_pos, d, M, position, cubie_index=None):
        pts3d_world = self.get_transformed_points(M, position)
        if pts3d_world.shape[0] < 3:
            return

        # Passage en coordonnées caméra
        pts3d = (R_view @ (pts3d_world - camera_pos).T).T

        # On enlève si un point est derrière la caméra
        if np.any(pts3d[:, 2] <= 1e-6):
            return

        # Calcul de la normale
        v0, v1, v2 = pts3d[0], pts3d[1], pts3d[2]
        n = np.cross(v1 - v0, v2 - v0)
        
        # Si la normale est nulle, on ne dessine pas la face
        if np.linalg.norm(n) < 1e-9:
            return
        
        # Centre de la face
        center = pts3d.mean(axis=0)
        
        # Epsilon pour éviter les erreurs numériques
        eps = 1e-6
        
        # Si la face est tournée vers la caméra, on la dessine sinon on ne fait rien
        if np.dot(n, center) < -eps:
            return

        # Projection perspective et dessin
        pts2d = project_perspective(pts3d, d=d)
        pygame.draw.polygon(surface, self.color, to_screen(pts2d))





        # --- Ajout affichage index ---
        if cubie_index is not None:
            font = pygame.font.SysFont(None, 24)
            text = font.render(str(cubie_index), True, (0,0,0))
            # Position du texte : centre de la face projetée
            center2d = project_perspective(center.reshape(1,3), d=d)[0]
            x, y = to_screen([center2d])[0]
            surface.blit(text, (x-10, y-10))