#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 27 13:53:56 2025

ce code crée un triangle et le fait tourner autour de l'origine
la séquence d'images est ensuite exportée dans une animation

@author: fehre
"""

import math

def Rotation(A, theta, x, y):
    """
    Calcule l'image d'un point ou d'un ensemble de points (x,y)
    par la rotation de centre A=(xA,yA) et d'angle theta (en radians).
    """
    xA, yA = A
    x_new, y_new = [], []
    for xi, yi in zip(x, y):
        x_rel, y_rel = xi - xA, yi - yA
        x_rot = x_rel * math.cos(theta) - y_rel * math.sin(theta)
        y_rot = x_rel * math.sin(theta) + y_rel * math.cos(theta)
        x_new.append(xA + x_rot)
        y_new.append(yA + y_rot)

    return x_new, y_new

# Exemple d'utilisation

A = (1, 1)            
theta = math.pi/2     
P = (2, 1)           

print(Rotation(A, theta, [P[0]], [P[1]])) 

# Pour faire tourner un triangle
A = (0, 0)
theta = math.pi/4  # 45°
x_points = [0, 1, 0]
y_points = [0, 0, 1]

x_rot, y_rot = Rotation(A, theta, x_points, y_points)
print(list(zip(x_rot, y_rot)))