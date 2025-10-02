import pygame
import numpy as np
from render3D.matrices import ROTATION_Y, ROTATION_X

class Camera:
    def __init__(self, position=[0.0, 0.0, 0.0], speed=3.0):
        self.position = np.array(position, dtype=float)
        self.speed = float(speed)

        self.yaw = 0.0
        self.pitch = 0.0
        self.rot_speed = 1.5  # rad/s

    def update(self, keys, dt):
        # Input de rotation
        if keys[pygame.K_LEFT]:
            self.yaw -= self.rot_speed * dt
        if keys[pygame.K_RIGHT]:
            self.yaw += self.rot_speed * dt
        if keys[pygame.K_UP]:
            self.pitch -= self.rot_speed * dt
        if keys[pygame.K_DOWN]:
            self.pitch += self.rot_speed * dt

        self.pitch = np.clip(self.pitch, -np.pi/2 + 1e-3, np.pi/2 - 1e-3)

        R_cam = ROTATION_Y(self.yaw) @ ROTATION_X(self.pitch) # Appliquer pitch puis yaw (les rotations)

        # Input de déplacement
        forward = R_cam @ np.array([0.0, 0.0, 1.0]) # axe Z caméra
        right   = R_cam @ np.array([1.0, 0.0, 0.0]) # axe X caméra
        up_world = np.array([0.0, 1.0, 0.0])  # axe Y global
        
        move = self.speed * dt
        if keys[pygame.K_y]:
            self.position += forward * move
        if keys[pygame.K_h]:
            self.position -= forward * move
        if keys[pygame.K_g]:
            self.position -= right * move
        if keys[pygame.K_j]:
            self.position += right * move
        if keys[pygame.K_SPACE]:
            self.position += up_world * move
        if keys[pygame.K_LCTRL]:
            self.position -= up_world * move