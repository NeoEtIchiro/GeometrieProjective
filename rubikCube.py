import pygame
import numpy as np
from math import pi
import copy

from render3D.matrices import *
from render3D.camera import Camera
from render3D.shapes import Cube
from render3D.utils import draw_scene

pygame.init()
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()
startTime = pygame.time.get_ticks()

# helper couleurs (RGB)
WHITE  = (255, 255, 255)
YELLOW = (255, 255,   0)
RED    = (180,   0,   0)
ORANGE = (255, 128,   0)
BLUE   = (0,   70, 255)
GREEN  = (0, 150,   0)
GRAY   = (80, 80, 80)
BLACK  = (0, 0, 0)

def color_from_normal(n):
    norm = np.linalg.norm(n)
    if norm < 1e-9:
        return None
    nn = n / norm
    axes = {
        (1,0,0): ORANGE,   # +X
        (-1,0,0): RED,     # -X
        (0,1,0): WHITE,    # +Y (up)
        (0,-1,0): YELLOW,  # -Y (down)
        (0,0,1): BLUE,     # +Z (front)
        (0,0,-1): GREEN    # -Z (back)
    }
    best_axis = None
    best_dot = 0.0
    for ax, col in axes.items():
        d = np.dot(nn, np.array(ax))
        if d > best_dot:
            best_dot = d
            best_axis = ax
    if best_dot > 0.6:
        return axes[best_axis]
    return None

def build_cubie(ix, iy, iz, spacing, center_z, cubie_size):
    pos = np.array([ix * spacing, iy * spacing, iz * spacing + center_z], dtype=float)
    cub = Cube(scale=cubie_size, position=pos.tolist(), angles=[0,0,0])
    # dupliquer les faces pour stickers
    orig_faces = getattr(cub, "faces", [])
    new_faces = []
    for f in orig_faces:
        nf = copy.deepcopy(f)
        nf.scale = cub.scale
        nf.angles = cub.angles
        nf.position = cub.position
        pts = nf.apply_transform()
        if pts.shape[0] < 3:
            nf.color = BLACK
            new_faces.append(nf)
            continue
        v0, v1, v2 = pts[0], pts[1], pts[2]
        n = np.cross(v1 - v0, v2 - v0)
        col = color_from_normal(n)
        nf.color = col if col is not None else BLACK
        new_faces.append(nf)
    cub.faces = new_faces
    # indices grille
    cub.grid = np.array([ix, iy, iz], dtype=int)
    return cub

class Rubik:
    def __init__(self, center_z=3.5, cubie_size=0.9, gap=0.06, turn_speed=6.0):
        self.center_z = center_z
        self.cubie_size = cubie_size
        self.gap = gap
        self.spacing = cubie_size + gap
        self.center = np.array([0.0, 0.0, center_z], dtype=float)
        self.turn_speed = float(turn_speed)  # rad/s
        self.cubies = []
        for ix in (-1, 0, 1):
            for iy in (-1, 0, 1):
                for iz in (-1, 0, 1):
                    self.cubies.append(build_cubie(ix, iy, iz, self.spacing, center_z, cubie_size))
        # état d'anim
        self.active = None   # dict: axis ('x','y','z'), layer (-1,0,1), dir (+1/-1), prog, affected, last_angle

    def grid_to_world(self, g):
        return np.array([g[0]*self.spacing, g[1]*self.spacing, g[2]*self.spacing + self.center_z], dtype=float)

    def rotate_vec(self, v, axis, angle):
        if axis == 'x':
            R = ROTATION_X(angle)
        elif axis == 'y':
            R = ROTATION_Y(angle)
        else:
            R = ROTATION_Z(angle)
        return R @ v

    def start_move(self, axis, layer, dir_sign):
        if self.active is not None:
            return False
        idx = {'x':0,'y':1,'z':2}[axis]
        affected = [c for c in self.cubies if c.grid[idx] == layer]
        if not affected:
            return False
        self.active = {
            'axis': axis,
            'idx': idx,
            'layer': layer,
            'dir': 1 if dir_sign >= 0 else -1,
            'prog': 0.0,
            'affected': affected,
            'last': 0.0,
        }
        return True

    def update(self, dt):
        if self.active is None:
            return
        a = self.active
        # progression
        a['prog'] += self.turn_speed * dt
        if a['prog'] > (pi/2):
            a['prog'] = pi/2
        delta = a['prog'] - a['last']
        a['last'] = a['prog']
        ang = delta * a['dir']

        # appliquer incrément d'angle aux cubies affectés
        for c in a['affected']:
            # tourner position autour du centre mondial
            v = c.position - self.center
            v = self.rotate_vec(v, a['axis'], ang)
            c.position = (self.center + v).astype(float)

            # tourner l'orientation autour de l'axe monde: ajouter sur l'axe correspondant
            if a['axis'] == 'x':
                c.angles[0] += ang
            elif a['axis'] == 'y':
                c.angles[1] += ang
            else:
                c.angles[2] += ang

        # fin de rotation: snap grille et angles
        if a['prog'] >= (pi/2 - 1e-6):
            for c in a['affected']:
                # snap angles sur l'axe tourné
                ax = a['axis']
                if ax == 'x':
                    c.angles[0] = round(c.angles[0] / (pi/2)) * (pi/2)
                elif ax == 'y':
                    c.angles[1] = round(c.angles[1] / (pi/2)) * (pi/2)
                else:
                    c.angles[2] = round(c.angles[2] / (pi/2)) * (pi/2)
                # maj indices grille
                gx, gy, gz = c.grid.tolist()
                if a['axis'] == 'y':
                    # rotation dans le plan (x,z)
                    if a['dir'] > 0:  # cw en regardant depuis +Y vers l'origine
                        gx, gz = -gz, gx
                    else:             # ccw
                        gx, gz = gz, -gx
                elif a['axis'] == 'x':
                    # rotation dans le plan (y,z)
                    if a['dir'] > 0:
                        gy, gz = gz, -gy
                    else:
                        gy, gz = -gz, gy
                else:  # 'z'
                    # rotation dans le plan (x,y)
                    if a['dir'] > 0:
                        gx, gy = gy, -gx
                    else:
                        gx, gy = -gy, gx
                c.grid = np.array([gx, gy, gz], dtype=int)
                # recalc position exacte depuis la grille (évite la dérive float)
                c.position = self.grid_to_world(c.grid)

            self.active = None  # mouvement terminé

# ---------- App setup ----------
rubik = Rubik(center_z=3.5, cubie_size=0.9, gap=0.06, turn_speed=6.0)
camera = Camera(position=[0.0, 0.0, -10.0], speed=3.0)

def handle_move_key(event):
    # Shift inverse le sens
    inv = -1 if (event.mod & pygame.KMOD_SHIFT) else +1
    key = event.key
    if key == pygame.K_u:   # Up (y = +1)
        rubik.start_move('y', +1, +inv)
    elif key == pygame.K_d: # Down (y = -1)
        rubik.start_move('y', -1, -inv)  # sens inversé pour cohérence visuelle
    elif key == pygame.K_l: # Left (x = -1)
        rubik.start_move('x', -1, +inv)
    elif key == pygame.K_r: # Right (x = +1)
        rubik.start_move('x', +1, -inv)
    elif key == pygame.K_f: # Front (z = +1)
        rubik.start_move('z', +1, +inv)
    elif key == pygame.K_b: # Back (z = -1)
        rubik.start_move('z', -1, -inv)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            handle_move_key(event)

    dt = clock.get_time() / 1000.0

    # inputs caméra
    keys = pygame.key.get_pressed()
    camera.update(keys, dt)

    # update rubik
    rubik.update(dt)

    # Clear screen
    screen.fill((50, 50, 50))

    # draw
    draw_scene(screen, rubik.cubies,
               camera_pos=camera.position,
               camera_angles=(camera.yaw, camera.pitch),
               d=10)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()