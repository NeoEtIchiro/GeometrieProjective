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
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import rc


## affichage d'un triangle
xtriangle = np.array([1,1.5,1.25])
ytriangle = np.array([1,1,1.5])

plt.figure(1)
plt.fill(xtriangle, ytriangle, facecolor='none', edgecolor='red')
plt.plot(xtriangle,ytriangle, '*')
plt.axis([-2,2,0,4])
plt.show()


# Rotation 
def RotationOrigine(t,x,y):
    # rotation d'angle t (en radians) autour de l'origine
    # appliquées aux points dont la liste des abscisses est x, et liste des ordonnées y
    M = np.array([[cos(t), -sin(t)],[sin(t),cos(t)]])
    v = np.array([x,y])  # on regroupe l'ensemble des points dans une matrice
    TriangleTourne = M.dot(v)
    return TriangleTourne

#%%# on crée les images de la sequence en les mettant dans un objet "list"
N=90  # nombre d'images dans la sequence
fig = plt.figure(2)
plt.axis('equal') # pour ne pas avoir l'impression que le triangle se déforme

angle_total = pi/2

liste_images = []
for j in range(N+1):
    v = RotationOrigine(angle_total*j/N,xtriangle,ytriangle)
    [xi,yi] = v
    im = plt.fill(xi, yi, facecolor='none', edgecolor='red')+plt.plot(xi,yi, 'bo')+plt.plot(0,0,'go')
    liste_images.append(im)


## export dans une animation gif
anim = animation.ArtistAnimation(fig, liste_images)#, interval=150, repeat_delay=1000)
anim.save("RotationTriangle1.gif")
rc('animation', html='jshtml')
anim