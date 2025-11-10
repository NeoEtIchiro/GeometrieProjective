import pygame # type: ignore
import numpy as np # type: ignore
from math import pi

from render3D.matrices import *
from render3D.camera import Camera
from render3D.shapes import Cube
from render3D.utils import draw_scene

from render3D.consts import *

pygame.init()
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()
startTime = pygame.time.get_ticks()

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




# ---------- App setup ----------
rubik = Rubik(gap=0.16, turn_speed=10.0)
camera = Camera(position=[0.0, 0.0, -15.0], speed=3.0)

def handle_move_key(event):
    inv = -1 if (event.mod & pygame.KMOD_SHIFT) else +1
    key = event.key
    if key == pygame.K_u:
        rubik.start_move('y', +1, +inv)
    elif key == pygame.K_d:
        rubik.start_move('y', -1, -inv)
    elif key == pygame.K_l:
        rubik.start_move('x', -1, +inv)
    elif key == pygame.K_r:
        rubik.start_move('x', +1, -inv)
    elif key == pygame.K_f:
        rubik.start_move('z', +1, +inv)
    elif key == pygame.K_b:
        rubik.start_move('z', -1, -inv)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            handle_move_key(event)

    dt = clock.get_time() / 1000.0
    keys = pygame.key.get_pressed()
    camera.update(keys, dt)
    rubik.update(dt)

    screen.fill((50, 50, 50))
    draw_scene(screen, rubik.cubies,
               camera_pos=camera.position,
               camera_angles=(camera.yaw, camera.pitch),
               d=10)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()