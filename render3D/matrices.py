from math import cos, sin
import numpy as np

def ROTATION_X(angle):
    return np.array([
        [1, 0, 0],
        [0, cos(angle), -sin(angle)],
        [0, sin(angle), cos(angle)]
    ])

def ROTATION_Y(angle):
    return np.array([
        [cos(angle), 0, sin(angle)],
        [0, 1, 0],
        [-sin(angle), 0, cos(angle)]
    ])

def ROTATION_Z(angle):
    return np.array([
        [cos(angle), -sin(angle), 0],
        [sin(angle), cos(angle), 0],
        [0, 0, 1]
    ])
    
def HOMOTHETIE(k):
    return np.array([
        [k, 0, 0],
        [0, k, 0],
        [0, 0, k]
    ])
    
def TRANSLATION(tx, ty):
    return np.array([
        [1, 0, tx],
        [0, 1, ty],
        [0, 0, 1]
    ])