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

def parse_move_string(s):
    """Retourne une liste de 1 ou 2 tuples (axis, layer, dir) selon la chaîne s."""
    s = s.strip()
    if not s:
        return []
    # mapping face -> (axis, layer, base_dir)
    # base_dir = +1 correspond à un quart de tour "horaire" vu de l'extérieur
    face_map = {
        'U': ('y', 1, +1),
        'D': ('y', -1, +1),
        'R': ('x', 1, +1),
        'L': ('x', -1, +1),
        'F': ('z', 1, +1),
        'B': ('z', -1, +1),
    }
    face = s[0].upper()
    if face not in face_map:
        raise ValueError(f"Unknown face '{face}' in move '{s}'")
    axis, layer, base = face_map[face]

    # detector suffix
    suffix = s[1:] if len(s) > 1 else ''
    moves = []
    if suffix == "2":
        # double = deux quarts de tour dans le même sens
        moves.append((axis, layer, base))
        moves.append((axis, layer, base))
    else:
        # prime (') inverse le sens
        if suffix == "'":
            moves.append((axis, layer, -base))
        else:
            moves.append((axis, layer, base))
    return moves

def parse_moves_list(strings):
    out = []
    for s in strings:
        out.extend(parse_move_string(s))
    return out