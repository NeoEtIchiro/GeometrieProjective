from render3D.shapes import Cube
from render3D.consts import *
from render3D.matrices import *
from render3D.utils import parse_moves_list

import numpy as np # type: ignore
from math import pi

def apply_rubik_sequences(rubik, cfg):
    rubik.input_buffer.clear()
    seqs = cfg.get('rubik', {}).get('sequences', [])
    for seq in seqs:
        speed = float(seq.get('speed', 1.0))
        moves_strings = seq.get('moves', [])
        moves = parse_moves_list(moves_strings)
        rubik.input_buffer.append(('SET_SPEED', speed))
        rubik.input_buffer.extend(moves)

def build_cubie(cubie_x, cubie_y, cubie_z, spacing):
    pos = np.array([cubie_x * spacing, cubie_y * spacing, cubie_z * spacing], dtype=float)
    cubie = Cube(scale=1, position=pos.tolist(), rotation_matrix=np.eye(3))

    # Ordre des faces dans Cube:
    # 0: z+, 1: z-, 2: x+, 3: x-, 4: y+, 5: y-
    gx, gy, gz = cubie_x, cubie_y, cubie_z
    for i, f in enumerate(cubie.faces):
        keep = (
            (i == 0 and gz == +1) or
            (i == 1 and gz == -1) or
            (i == 2 and gx == +1) or
            (i == 3 and gx == -1) or
            (i == 4 and gy == +1) or
            (i == 5 and gy == -1)
        )
        if not keep:
            f.color = BLACK  # face intérieure non visible

    cubie.grid = np.array([cubie_x, cubie_y, cubie_z], dtype=int)
    return cubie

class Rubik:
    def __init__(self, gap=1.2, turn_speed=2.0):
        self.gap = gap
        self.spacing = 1 + gap
        self.turn_speed = float(turn_speed)
        self.cubies = []

        for ix in (-1, 0, 1):
            for iy in (-1, 0, 1):
                for iz in (-1, 0, 1):
                    self.cubies.append(build_cubie(ix, iy, iz, self.spacing))
        
        self.moveState = None
        self.input_buffer = []

    def grid_to_world(self, grid):
        return np.array([grid[0]*self.spacing, grid[1]*self.spacing, grid[2]*self.spacing], dtype=float)

    def rotate_vec(self, v, axis, angle):
        if axis == 'x':
            R = ROTATION_X(angle)
        elif axis == 'y':
            R = ROTATION_Y(angle)
        else:
            R = ROTATION_Z(angle)
        return R @ v

    def start_move(self, axis, layer, dir_sign):
        if self.moveState is not None:
            # Ajoute à l'input buffer si une rotation est en cours
            self.input_buffer.append((axis, layer, dir_sign))
            return False
        
        idx = {'x':0,'y':1,'z':2}[axis]
        affected = [cubie for cubie in self.cubies if cubie.grid[idx] == layer]
        if not affected:
            return False
        self.moveState = {
            'axis': axis,
            'idx': idx,
            'layer': layer,
            'rotationDir': 1 if dir_sign >= 0 else -1,
            'affected': affected,
            'progression': 0.0,
            'lastProgression': 0.0,
        }
        return True

    def update(self, dt):
        # Si aucun mouvement en cours, démarre le prochain du buffer s'il y en a un
        while self.moveState is None and self.input_buffer:
            item = self.input_buffer.pop(0)
            if isinstance(item, tuple) and len(item) == 2 and item[0] == 'SET_SPEED':
                self.turn_speed = float(item[1])
                continue
            axis, layer, dir_sign = item
            self.start_move(axis, layer, dir_sign)
            break
        if self.moveState is None:
            return
        
        moveState = self.moveState
        moveState['progression'] += self.turn_speed * dt
        if moveState['progression'] > (pi/2):
            moveState['progression'] = pi/2
        
        delta = moveState['progression'] - moveState['lastProgression']
        moveState['lastProgression'] = moveState['progression']
        angle = delta * moveState['rotationDir']

        # Appliquer rotation incrémentale globale (position + orientation)
        for cubie in moveState['affected']:
            cubie.position = self.rotate_vec(cubie.position, moveState['axis'], angle).astype(float)
            # Orientation: composition par rotation GLOBALE (matrice)
            if moveState['axis'] == 'x':
                R_global = ROTATION_X(angle)
            elif moveState['axis'] == 'y':
                R_global = ROTATION_Y(angle)
            else:
                R_global = ROTATION_Z(angle)
            cubie.rotation_matrix = R_global @ cubie.rotation_matrix

        # Fin de rotation: snapping
        if moveState['progression'] >= (pi/2 - 1e-6):
            for cubie in moveState['affected']:
                grid_x, grid_y, grid_z = cubie.grid.tolist()
                if moveState['axis'] == 'y':
                    if moveState['rotationDir'] > 0:
                        grid_x, grid_z = grid_z, -grid_x
                    else:
                        grid_x, grid_z = -grid_z, grid_x
                elif moveState['axis'] == 'x':
                    if moveState['rotationDir'] > 0:
                        grid_y, grid_z = -grid_z, grid_y
                    else:
                        grid_y, grid_z = grid_z, -grid_y
                else:  # 'z'
                    if moveState['rotationDir'] > 0:
                        grid_x, grid_y = -grid_y, grid_x
                    else:
                        grid_x, grid_y = grid_y, -grid_x

                cubie.grid = np.array([grid_x, grid_y, grid_z], dtype=int)
                cubie.position = self.grid_to_world(cubie.grid)

                # Snap robuste : trouve la matrice de rotation la plus proche parmi toutes les combinaisons de quarts de tour
                M = cubie.rotation_matrix
                best_M = None
                best_dist = float('inf')
                for x in [0, 0.5*pi, pi, 1.5*pi]:
                    for y in [0, 0.5*pi, pi, 1.5*pi]:
                        for z in [0, 0.5*pi, pi, 1.5*pi]:
                            M_candidate = ROTATION_Y(y) @ ROTATION_X(x) @ ROTATION_Z(z)
                            dist = np.linalg.norm(M - M_candidate)
                            if dist < best_dist:
                                best_dist = dist
                                best_M = M_candidate
                cubie.rotation_matrix = best_M

            self.moveState = None
            # Dès qu'une rotation est terminée, traite le prochain input du buffer
            if self.input_buffer:
                # Support de commandes spéciales dans le buffer, ex: ('SET_SPEED', value)
                while self.input_buffer:
                    item = self.input_buffer.pop(0)
                    if isinstance(item, tuple) and len(item) == 2 and item[0] == 'SET_SPEED':
                        self.turn_speed = float(item[1])
                        # continue pour traiter l'item suivant (si c'est un mouvement)
                        continue
                    # sinon c'est un mouvement (axis, layer, dir_sign)
                    axis, layer, dir_sign = item
                    self.start_move(axis, layer, dir_sign)
                    break