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

def draw_scene(surface, objects, camera_pos, camera_angles, d=10):
    yaw, pitch = camera_angles
    R_cam = ROTATION_Y(yaw) @ ROTATION_X(pitch)
    R_view = R_cam.T

    faces_to_draw = []
    for obj in objects:
        M = obj.get_transform_matrix()
        for face in obj.faces:
            # Transformation globale
            pts3d_world = face.get_transformed_points(M, obj.position)
            # Passage en coordonnées caméra
            pts3d_cam = (R_view @ (pts3d_world - camera_pos).T).T
            # Calcul profondeur moyenne (z caméra)
            z_mean = np.mean(pts3d_cam[:, 2])
            faces_to_draw.append((z_mean, face, pts3d_cam, obj, M, obj.position))

    # Trier du plus loin au plus proche
    faces_to_draw.sort(key=lambda tup: tup[0], reverse=True)

    for _, face, pts3d_cam, obj, M, position in faces_to_draw:
        # On ne redonne pas pts3d_cam à face.draw, car elle refait le calcul
        face.draw(surface, R_view, camera_pos, d, M, position)