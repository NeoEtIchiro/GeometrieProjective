import numpy as np
from render3D.matrices import ROTATION_Y, ROTATION_X

def to_screen(points, center=(300, 300), scale=100):
    # Convertit les points mathématiques en pixels pour Pygame
    return [(int(center[0] + scale*x), int(center[1] - scale*y)) for x, y in points]

def project_perspective(points3d, d=10):
    # Projection perspective simple
    projected = []
    
    # On projette chaque point
    for x, y, z in points3d:
        # On évite la division par zéro
        factor = d / z
        
        # On projette
        projected.append([x * factor, y * factor])
    
    return np.array(projected)

def draw_scene(surface, shapes, camera_pos=np.array([0.0, 0.0, 0.0]), camera_angles=(0.0, 0.0), d=10):
    """
    Painter's algorithm:
    - world -> camera space
    - tri du plus loin (grand z) au plus proche (petit z)
    """
    yaw, pitch = camera_angles
    R_cam = ROTATION_Y(yaw) @ ROTATION_X(pitch)
    R_view = R_cam.T

    faces_depth = []
    for shape in shapes:
        for face in shape.faces:
            face.scale = shape.scale
            face.angles = shape.angles
            face.position = shape.position
            pts3d_world = face.apply_transform()

            center_cam = (R_view @ (pts3d_world.mean(axis=0) - camera_pos))
            depth = center_cam[2]
            faces_depth.append((depth, face))

    # Dessiner du plus loin au plus proche
    faces_depth.sort(key=lambda x: x[0], reverse=True)
    for _, face in faces_depth:
        face.draw(surface, R_view=R_view, camera_pos=camera_pos, d=d)