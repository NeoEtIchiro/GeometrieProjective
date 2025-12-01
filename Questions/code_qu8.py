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

def Rotation2(A, theta, x, y):
    """
    Calcule l'image d'un point ou d'un ensemble de points (x,y)
    par la rotation de centre A=(xA,yA) et d'angle theta (en radians),
    en utilisant les coordonnées homogènes.
    """
    xA, yA = A
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    x_new, y_new = [], []
    for xi, yi in zip(x, y):
        # Coordonnées homogènes du point
        X = xi
        Y = yi
        W = 1
        # Matrice de rotation homogène autour de A
        X_rot = cos_t*X - sin_t*Y + xA - xA*cos_t + yA*sin_t
        Y_rot = sin_t*X + cos_t*Y + yA - xA*sin_t - yA*cos_t
        x_new.append(X_rot)
        y_new.append(Y_rot)
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

# Exemple d'utilisation de Rotation2
A = (1, 1)
theta = math.pi/2
P = (2, 1)

print(Rotation2(A, theta, [P[0]], [P[1]]))

# Pour faire tourner un triangle avec Rotation2
A = (0, 0)
theta = math.pi/4  # 45°
x_points = [0, 1, 0]
y_points = [0, 0, 1]
x_rot, y_rot = Rotation2(A, theta, x_points, y_points)
print(list(zip(x_rot, y_rot)))