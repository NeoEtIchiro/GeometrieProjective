import matplotlib.pyplot as plt
import numpy as np
from math import pi, cos, sin
import matplotlib.animation as animation

def ROTATION(t):
    return np.array(
        [[cos(t), -sin(t)],
         [sin(t), cos(t)]]
    )

def HOMOTHETIE(k):
    return np.array(
        [[k, 0],
         [0, k]]
    )

class Polygon:
    def __init__(self, ax, x, y, color='red'):
        self.x = x
        self.y = y
        self.color = color
        self.ax = ax
        self.patch = ax.fill(self.x, self.y, facecolor='none', edgecolor=color)[0]
    
    def transform(self, Ms, values):
        for M, value in zip(Ms, values):
            M = M(value)
            v = np.array([self.x, self.y])
            transformed = M.dot(v)
            return transformed[0], transformed[1]


fig, ax = plt.subplots()
ax.set_aspect('equal')
ax.set_xlim(-4, 4)
ax.set_ylim(-4, 4)

# Initial shape
square = Polygon(ax, np.array([1, 1.5, 1.5, 1]), np.array([1, 1, 1.5, 1.5]), 'red')
triangle = Polygon(ax, np.array([0, 1, 0]), np.array([0, 0, 1]), 'blue')

FRAME_COUNT = 90

def animate(i):
    angle = i * (2 * pi / FRAME_COUNT)
    size = 1 + (i * 2 / FRAME_COUNT)  # commence à 1, finit à 3
    # Compose la matrice homothétie puis rotation
    M = HOMOTHETIE(size) @ ROTATION(angle)
    v = np.array([square.x, square.y])
    transformed = M.dot(v)
    xi, yi = transformed[0], transformed[1]
    square.patch.set_xy(np.column_stack([xi, yi]))
    return (square.patch,)

def animateTriangle(i):
    size = (i - FRAME_COUNT/2) * (3 / FRAME_COUNT)
    xi, yi = square.transform(HOMOTHETIE, size)
    square.patch.set_xy(np.column_stack([xi, yi]))
    return (square.patch)

ani = animation.FuncAnimation(fig, animate, frames=FRAME_COUNT+1, interval=1)
# ani2 = animation.FuncAnimation(fig, animateTriangle, frames=FRAME_COUNT+1, interval=1)

plt.show()

# Animation parameters
# FRAME_COUNT = 90
# angle_total = 2 * pi

# Initial plot
# square_patch = ax.fill(square.x, square.y, facecolor='none', edgecolor='red')[0]
# points_plot, = ax.plot(square.x, square.y, 'bo')
# origin_plot, = ax.plot(0, 0, 'go')

# def animate(j):
#     v = square.rotate(angle_total * j / FRAME_COUNT)
#     xi, yi = v.x, v.y
#     square_patch.set_xy(np.column_stack([xi, yi]))
#     points_plot.set_data(xi, yi)
#     # origin_plot stays the same
#     return square_patch, points_plot, origin_plot

# ani = animation.FuncAnimation(fig, animate, frames=FRAME_COUNT+1, interval=50, blit=True)

# # Pour afficher l'animation dans la fenêtre interactive


# # Pour sauvegarder en GIF
# ani.save("RotationTriangle1.gif", writer='pillow')