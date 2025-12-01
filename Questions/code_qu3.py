
import matplotlib.pyplot as plt
import numpy as np
from math import pi, cos, sin
import matplotlib.animation as animation

# Triangle initial
xtriangle = np.array([1, 1.5, 1.25, 1])
ytriangle = np.array([1, 1, 1.5, 1.5])

# Fonction pour effectuer une rotation autour d'un centre donné
def Rotation(t, x, y, xc, yc):
    M = np.array([[cos(t), -sin(t)],
                  [sin(t), cos(t)]])
    v = np.array([x - xc,
                  y - yc])
    v_rotated = M.dot(v)
    return v_rotated[0] + xc, v_rotated[1] + yc

# Fonction pour effectuer une homothétie de centre donné
def Homothetie(k, x, y, xc, yc):
    return k * (x - xc) + xc, k * (y - yc) + yc

# Fonction pour effectuer une translation
def Translation(dx, dy, x, y):
    return x + dx, y + dy

# Fonction pour composer plusieurs transformations
def ComposeTransformations(x, y, transformations):
    for transform in transformations:
        x, y = transform(x, y)
    return x, y

# Animation parameters
N = 90
angle_total = 2*pi / 2
scale_factor = 5
translation_vector = (0.5, 0.5)

fig, ax = plt.subplots()
ax.set_aspect('equal')
ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)

# Initial plot
triangle_patch = ax.fill(xtriangle, ytriangle, facecolor='none', edgecolor='red')[0]
points_plot, = ax.plot(xtriangle, ytriangle, 'bo')
origin_plot, = ax.plot(0, 0, 'go')

# Fonction d'animation
def animate(j):
    t = angle_total * j / N
    k = 1 + (scale_factor - 1) * j / N
    dx, dy = translation_vector[0] * j / N, translation_vector[1] * j / N

    transformations = [
        lambda x, y: Rotation(t, x, y, 0, 0),
        lambda x, y: Homothetie(k, x, y, 0, 0),
        lambda x, y: Translation(dx, dy, x, y)
    ]

    xi, yi = ComposeTransformations(xtriangle, ytriangle, transformations)
    triangle_patch.set_xy(np.column_stack([xi, yi]))
    points_plot.set_data(xi, yi)
    return triangle_patch, points_plot, origin_plot

ani = animation.FuncAnimation(fig, animate, frames=N+1, interval=50, blit=True)

# Pour afficher l'animation dans la fenêtre interactive
plt.show()

# Pour sauvegarder en GIF
ani.save("TransformationTriangle.gif", writer='pillow')