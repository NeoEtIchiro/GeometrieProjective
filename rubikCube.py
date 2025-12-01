import random
import pygame # type: ignore
import numpy as np # type: ignore
import commentjson as json
import os

from render3D.matrices import *
from render3D.camera import Camera, apply_camera_sequences

from render3D.utils import *

from render3D.consts import *

from render3D.rubik import Rubik, apply_rubik_sequences

# ---------- App setup ----------
# Init
pygame.init()
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()
startTime = pygame.time.get_ticks()
cfg_path = os.path.join(os.path.dirname(__file__), "config.jsonc")

# Rubik init
rubik = Rubik(gap=0.05)

if os.path.exists(cfg_path):
    with open(cfg_path, 'r') as f:
        cfg = json.load(f)
    apply_rubik_sequences(rubik, cfg)


# Camera init
camera = Camera(position=[0.0, 0.0, -15.0], speed=5.0)
camera.start_orbit(radius=20.0, ang_speed=0.7, vert_amp=7.5, vert_speed=0.9)

if os.path.exists(cfg_path):
    with open(cfg_path, 'r') as f:
        cfg = json.load(f)
    apply_camera_sequences(camera, cfg)


# Main loop
running = True
while running:
    # Quiting
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update
    delta_time = clock.get_time() / 1000.0
    camera.update(delta_time)
    rubik.update(delta_time)

    # Draw
    screen.fill((50, 50, 50))
    draw_scene(screen, rubik.cubies, camera_pos=camera.position, camera_angles=(camera.yaw, camera.pitch))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
