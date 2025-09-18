import pygame
import numpy as np
from render3D.matrices import ROTATION_Y, ROTATION_X

class Camera:
    def __init__(self, position=[0.0, 0.0, 0.0], speed=3.0):
        self.position = np.array(position, dtype=float)
        self.speed = float(speed)
        # si besoin, ajouter yaw/pitch pour rotation plus tard
        self.yaw = 0.0
        self.pitch = 0.0

    def update(self, keys, dt):
        rot_speed = -1.5  # rad/s
        if keys[pygame.K_LEFT]:
            self.yaw += rot_speed * dt
        if keys[pygame.K_RIGHT]:
            self.yaw -= rot_speed * dt
        if keys[pygame.K_UP]:
            self.pitch += rot_speed * dt
        if keys[pygame.K_DOWN]:
            self.pitch -= rot_speed * dt

        self.pitch = np.clip(self.pitch, -np.pi/2 + 1e-3, np.pi/2 - 1e-3)

        R_cam = ROTATION_Y(self.yaw) @ ROTATION_X(self.pitch)
        forward = R_cam @ np.array([0.0, 0.0, 1.0])
        right   = R_cam @ np.array([1.0, 0.0, 0.0])
        up_world = np.array([0.0, 1.0, 0.0])  # axe Y global

        move = self.speed * dt
        if keys[pygame.K_z]:
            self.position += forward * move
        if keys[pygame.K_s]:
            self.position -= forward * move
        if keys[pygame.K_q]:
            self.position -= right * move
        if keys[pygame.K_d]:
            self.position += right * move
        if keys[pygame.K_SPACE]:
            self.position += up_world * move     # monter dans le monde
        if keys[pygame.K_LCTRL]:
            self.position -= up_world * move     # descendre dans le monde