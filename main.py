import pygame
import numpy as np
from math import pi

from render3D.matrices import *
from render3D.camera import Camera

from render3D.shapes import Cube

from render3D.utils import draw_scene

pygame.init()
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()
startTime = pygame.time.get_ticks()

cube = Cube(scale=1, position=[0, 0, 0], angles=[0, 0, 0])
cube2 = Cube(scale=1, position=[2, 0, -1], angles=[0, 0, 0])

# instancier la caméra
camera = Camera(position=[0.0, 0.0, -10.0], speed=3.0)

running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
                
    # delta time en secondes (utilise le temps passé entre frames)
    dt = clock.get_time() / 1000.0

    # inputs clavier gérés par la caméra
    keys = pygame.key.get_pressed()
    camera.update(keys, dt)

    # Clear screen
    screen.fill((255, 255, 255))

    # Calculate actual time in seconds
    actTime = (pygame.time.get_ticks() - startTime) / 1000

    cube.angles[1] += 0.01
    cube.angles[0] += 0.005
    cube.position[0] = 0.5 * np.sin(actTime * 0.5 * np.pi)
    cube.position[1] = 0.5 * np.cos(actTime * 0.5 * np.pi)
    cube.position[2] = 5 * np.sin(actTime * 0.5 * np.pi)

    # draw_scene utilise maintenant la position + l'orientation de la caméra
    draw_scene(screen, [cube, cube2],
               camera_pos=camera.position,
               camera_angles=(camera.yaw, camera.pitch),
               d=10)

    # Refresh display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()