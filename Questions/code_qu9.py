#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 27 13:53:56 2025

ce code crée un triangle et le fait tourner autour de l'origine
la séquence d'images est ensuite exportée dans une animation

@author: fehren
"""

import matplotlib.pyplot as plt
import numpy as np
from math import pi, cos, sin
import matplotlib.animation as animation
from code_qu8 import Rotation2

# Triangle initial
xtriangle = np.array([1, -1.2, 2])
ytriangle = np.array([2, 1.3, 0.5])

# Animation parameters
N = 90
angle_total = 2*pi

fig, ax = plt.subplots()
ax.set_aspect('equal')
ax.set_xlim(-2, 2)
ax.set_ylim(0, 4)

# Initial plot
triangle_patch = ax.fill(xtriangle, ytriangle, facecolor='none', edgecolor='red')[0]
points_plot, = ax.plot(xtriangle, ytriangle, 'bo')
origin_plot, = ax.plot(0, 0, 'go')

def animate(j):
    A = (xtriangle[0], ytriangle[0])
    xi, yi = Rotation2(A, angle_total * j / N, xtriangle, ytriangle)
    triangle_patch.set_xy(np.column_stack([xi, yi]))
    points_plot.set_data(xi, yi)
    # origin_plot stays the same
    return triangle_patch, points_plot, origin_plot

ani = animation.FuncAnimation(fig, animate, frames=N+1, interval=50, blit=True)

# Pour afficher l'animation dans la fenêtre interactive
plt.show()

# Pour sauvegarder en GIF
ani.save("RotationTriangle2.gif", writer='pillow')