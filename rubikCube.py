import pygame # type: ignore
import numpy as np # type: ignore
from math import pi
import copy

from render3D import face
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
    cubie = Cube(scale=1, position=pos.tolist(), angles=[0,0,0])
    
    orig_faces = getattr(cubie, "faces", [])
    new_faces = []
    # Convention: faces = [x+, x-, y+, y-, z+, z-]
    for i, face in enumerate(orig_faces):
        new_face = copy.deepcopy(face)
        new_face.scale = cubie.scale
        new_face.angles = cubie.angles
        new_face.position = cubie.position

        # Coloration selon la position du cubie
        if i == 0 and cubie_z == 1:      # x+
            pass  # garder la couleur
        elif i == 1 and cubie_z == -1:   # x-
            pass
        elif i == 2 and cubie_x == 1:    # y+
            pass
        elif i == 3 and cubie_x == -1:   # y-
            pass
        elif i == 4 and cubie_y == 1:    # z+
            pass
        elif i == 5 and cubie_y == -1:   # z-
            pass
        else:
            new_face.color = BLACK  # face intérieure

        new_faces.append(new_face)
    cubie.faces = new_faces
    cubie.grid = np.array([cubie_x, cubie_y, cubie_z], dtype=int)
    return cubie

class Rubik:
    def __init__(self, gap=0.06, turn_speed=6.0):
        self.gap = gap

        # espacement entre centres des cubies
        self.spacing = 1 + gap

        self.turn_speed = float(turn_speed)

        self.cubies = []

        # construire les 27 cubies, passe à travers -1,0,1 en x,y,z
        for ix in (-1, 0, 1):
            for iy in (-1, 0, 1):
                for iz in (-1, 0, 1):
                    self.cubies.append(build_cubie(ix, iy, iz, self.spacing))
        
        self.moveState = None

    def grid_to_world(self, grid):
        # Retourne la position 3D (float) du centre du cubie à partir de ses indices grille (int)
        return np.array([grid[0]*self.spacing, grid[1]*self.spacing, grid[2]*self.spacing], dtype=float)

    def rotate_vec(self, v, axis, angle):
        # Rotate un vecteur en fonction de l'axe et de l'angle
        if axis == 'x':
            R = ROTATION_X(angle)
        elif axis == 'y':
            R = ROTATION_Y(angle)
        else:
            R = ROTATION_Z(angle)
        return R @ v

    def rotate_vec_local(self, v, axis, angle, cubie_angles):
        # Applique la rotation autour de l'axe donné, dans le repère local du cubie
        # 1. Transforme le vecteur dans le repère local
        # 2. Applique la rotation
        # 3. Re-transforme dans le repère global

        # Matrice de rotation locale (cubie avant rotation)
        M_local = ROTATION_Y(cubie_angles[1]) @ ROTATION_X(cubie_angles[0]) @ ROTATION_Z(cubie_angles[2])
        # Inverse pour repasser dans le repère du cubie
        M_local_inv = np.linalg.inv(M_local)

        # Passe v dans le repère local
        v_local = M_local_inv @ v

        # Applique la rotation autour de l'axe local
        if axis == 'x':
            R = ROTATION_X(angle)
        elif axis == 'y':
            R = ROTATION_Y(angle)
        else:
            R = ROTATION_Z(angle)
        v_local_rot = R @ v_local

        # Repasse dans le repère global
        v_global = M_local @ v_local_rot
        return v_global

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
        
        # On ajoute à la progression de la rotation
        moveState['progression'] += self.turn_speed * dt

        # Clamp à 90° pour ne pas trop tourner
        if moveState['progression'] > (pi/2):
            moveState['progression'] = pi/2
        
        # Incrément d'angle depuis la dernière frame
        delta = moveState['progression'] - moveState['lastProgression']

        moveState['lastProgression'] = moveState['progression']

        # Angle à appliquer (positif ou négatif selon le sens)
        angle = delta * moveState['rotationDir']

        # Appliquer incrément d'angle aux cubies affectés
        for cubie in moveState['affected']:
            v = self.rotate_vec(cubie.position, moveState['axis'], angle)
            cubie.position = v.astype(float)

            # Tourner l'orientation autour de l'axe monde: ajouter sur l'axe correspondant
            if moveState['axis'] == 'x':
                cubie.angles[0] += angle
            elif moveState['axis'] == 'y':
                cubie.angles[1] += angle
            else:
                cubie.angles[2] += angle

        # Fin de rotation: snap grille et angles
        if moveState['progression'] >= (pi/2 - 1e-6):
            for cubie in moveState['affected']:
                # Snap angles sur l'axe tourné
                ax = moveState['axis']
                if ax == 'x':
                    cubie.angles[0] = round(cubie.angles[0] / (pi/2)) * (pi/2)
                elif ax == 'y':
                    cubie.angles[1] = round(cubie.angles[1] / (pi/2)) * (pi/2)
                else:
                    cubie.angles[2] = round(cubie.angles[2] / (pi/2)) * (pi/2)

                
                # Maj indices grille
                grid_x, grid_y, grid_z = cubie.grid.tolist()
                if moveState['axis'] == 'y':
                    # rotation dans le plan (x,z)
                    if moveState['rotationDir'] > 0:  # cw en regardant depuis +Y vers l'origine
                        grid_x, grid_z = grid_z, -grid_x
                    else:             # ccw
                        grid_x, grid_z = -grid_z, grid_x
                elif moveState['axis'] == 'x':
                    # rotation dans le plan (y,z)
                    if moveState['rotationDir'] > 0:
                        grid_y, grid_z = -grid_z, grid_y
                    else:
                        grid_y, grid_z = grid_z, -grid_y
                else:  # 'z'
                    # rotation dans le plan (x,y)
                    if moveState['rotationDir'] > 0:
                        grid_x, grid_y = -grid_y, grid_x
                    else:
                        grid_x, grid_y = grid_y, -grid_x


                cubie.grid = np.array([grid_x, grid_y, grid_z], dtype=int)
                # recalc position exacte depuis la grille (évite la dérive float)
                cubie.position = self.grid_to_world(cubie.grid)

            self.moveState = None  # mouvement terminé

    def apply_global_rotation_to_local_angles(cubie, axis, angle):
        # 1. Matrice de rotation locale actuelle
        M_local = ROTATION_Y(cubie.angles[1]) @ ROTATION_X(cubie.angles[0]) @ ROTATION_Z(cubie.angles[2])
        # 2. Matrice de rotation globale à appliquer
        if axis == 'x':
            R_global = ROTATION_X(angle)
        elif axis == 'y':
            R_global = ROTATION_Y(angle)
        else:
            R_global = ROTATION_Z(angle)
        # 3. Nouvelle orientation
        M_new = R_global @ M_local
        # 4. Extraire les angles d'Euler (sans scipy, version simple pour petits angles)
        # Attention : cette extraction est simplifiée et peut ne pas couvrir tous les cas
        sy = np.sqrt(M_new[0,0]**2 + M_new[1,0]**2)
        singular = sy < 1e-6
        if not singular:
            x = np.arctan2(M_new[2,1], M_new[2,2])
            y = np.arctan2(-M_new[2,0], sy)
            z = np.arctan2(M_new[1,0], M_new[0,0])
        else:
            x = np.arctan2(-M_new[1,2], M_new[1,1])
            y = np.arctan2(-M_new[2,0], sy)
            z = 0
        cubie.angles = [x, y, z]


# ---------- App setup ----------
rubik = Rubik(gap=0.06, turn_speed=12.0)
camera = Camera(position=[0.0, 0.0, -15.0], speed=3.0)

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