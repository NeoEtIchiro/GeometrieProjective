## 1 — Vue d’ensemble du projet

- Application Python utilisant Pygame pour afficher une représentation 3D d’un Rubik’s cube 3×3×3.
- Architecture modulaire : rendu et utilitaires dans `render3D` (matrices de transformation, formes, caméra, utilitaires de dessin) ; logique du rubik dans `rubikCube.py`.
- Chaque petit cube (« cubie ») est un objet graphique (classe Cube) avec : position 3D (vecteur), matrice d’orientation 3×3 (`rotation_matrix`), coordonnées discrètes de grille (`grid` ∈ {−1,0,1}^3) et faces colorées (les faces intérieures sont mises en noir).
- L’objet `Rubik` gère la collection des cubies, l’espacement (`gap`), la vitesse d’animation (`turn_speed`), l’état d’une rotation en cours (`moveState`) et un buffer d’entrées (`input_buffer`).

## 2 — Construction des cubies et gestion de l’échelle (homothétie)

- Chaque cubie est placé initialement en multipliant sa coordonnée de grille par `spacing = 1 + gap` : position_monde = grid × spacing.
- Homothétie / échelle gérées sur deux niveaux :
	- homothétie locale (`scale`) : paramètre dans la forme `Cube` qui définit la taille géométrique du cubie ;
	- homothétie globale / espacement (`gap` → `spacing`) : définit la distance entre centres de cubies et l’effet d’interstice.
- *Réponse à la question 1 — matrice de l’homothétie* : l’homothétie de rapport λ s’exprime par λ·I. En R² : H_λ = λ I₂ ; en R³ : H_λ = λ I₃. Dans le projet, l’effet d’un facteur d’échelle sur les positions est réalisé par multiplication par `spacing` (homothétie isotrope des positions).

## 3 — Rotations : principe et implémentation

- Les rotations sont effectuées avec des matrices de rotation 3×3 (fonctions ROTATION_X / ROTATION_Y / ROTATION_Z du module `render3D.matrices`).
- Sélection des cubies affectés : on filtre la liste des cubies par la coordonnée de grille sur l’axe donné (par exemple `grid[x] == +1` pour la face droite).
- Application incrémentale pour animer un quart de tour :
	- `moveState` conserve la progression (angle accumulé), la direction (±1), la liste des cubies affectés et la progression précédente (`lastProgression`) ;
	- à chaque frame : `progression += turn_speed * dt` (limité à π/2) ; `delta = progression - lastProgression` ; `angle = delta × rotationDir` ;
	- pour chaque cubie affecté on applique :
		- `position_monde = R_global(angle) @ position_monde` (rotation autour de l’origine),
		- `rotation_matrix = R_global(angle) @ rotation_matrix` (composition de l’orientation locale).
- Les rotations sont faites autour du centre du cube (l’origine), ce qui est cohérent puisque les positions des cubies sont définies relativement à ce centre.

## 5 — Buffer d’entrées et enchaînement des mouvements

- Si une rotation est déjà en cours, toute commande supplémentaire est ajoutée à `input_buffer` (FIFO).
- Après chaque rotation terminée, l’élément suivant du buffer est extrait et la rotation suivante démarre automatiquement. Cela permet de taper plusieurs mouvements rapidement et d’implémenter un scramble qui enfile une longue séquence de mouvements.

## 6 — Translations et coordonnées homogènes

- Les translations pures ne sont pas des applications linéaires en coordonnées cartésiennes (elles ne fixent pas l’origine). Cependant, en coordonnées homogènes on peut représenter les translations par multiplication matricielle.
- *Réponse à la question 2 — translation et matrice* : une translation ne s’écrit pas comme une matrice 2×2 en coordonnées cartésiennes ; en coordonnées homogènes (x, y, 1) on représente une translation par une matrice 3×3.
- *Réponse à la question 7 — vérification en coordonnées homogènes* : en coordonnées homogènes, un point P = (x, y, 1)^T et la matrice de translation
	T = [[1, 0, t_x], [0, 1, t_y], [0, 0, 1]]
	donnent T·P = (x + t_x, y + t_y, 1), ce qui correspond exactement à la translation souhaitée. Dans le projet, les rotations sont appliquées directement comme des transformations linéaires 3×3 sur des vecteurs 3D ; les coordonnées homogènes 4×4 seraient utiles si l’on voulait combiner translations et rotations en une seule matrice 4×4 pour pipeline matriciel 3D.

## 7 — Rotation autour d’un centre A ≠ O

- Dans le code, les rotations sont effectuées autour de l’origine. Pour faire une rotation autour d’un centre A = (x_A, y_A) on utilise la formule :

	P' = A + R(θ) · (P − A)

	Ce qui revient à : translation de −A, rotation autour de l’origine, puis translation de +A.

- *Réponse à la question 4 — expression via translations* : la rotation de centre A et d’angle θ s’écrit exactement comme ci‑dessus. Pour des animations centrées sur une face du cube, on peut translater temporairement les positions concernées, appliquer la rotation puis translater de retour, ou utiliser des matrices homogènes 4×4 pour combiner ces étapes.


## 9 — Fonctionnalités offertes

- Construction automatique d’un Rubik 3×3×3 avec affectation correcte des couleurs pour les faces externes.
- Rotations animées de couches (quart de tour) avec interpolation temporelle et snapping final précis.
- File d’attente d’actions (`input_buffer`) pour enchaîner des mouvements et scramble automatique.
- Réglage du `gap` (interstice) et du `scale` du cubie.
- Caméra mobile pour inspecter la scène depuis différents angles.

## 10 — Contrôles clavier (raccourcis principaux)

- `u` : tourner la couche « up » (axe y, couche +1) — `Shift` inverse le sens
- `d` : tourner la couche « down » (axe y, couche −1) — `Shift` inverse
- `l` : tourner la couche « left » (axe x, couche −1) — `Shift` inverse
- `r` : tourner la couche « right » (axe x, couche +1) — `Shift` inverse
- `f` : tourner la face « front » (axe z, couche +1) — `Shift` inverse
- `b` : tourner la face « back » (axe z, couche −1) — `Shift` inverse
- `m` : scramble automatique (génère une séquence aléatoire et l’ajoute au buffer)


## Conclusion

Le projet fournit une simulation visuelle et interactive d’un Rubik’s cube, structurée autour de transformations matricielles et d’un mécanisme simple et robuste d’animation incrémentale avec snapping final. L’homothétie est gérée par la combinaison `scale` (taille locale) et `spacing` (distance entre centres), tandis que les rotations utilisent des matrices 3×3 et un système d’input buffering pour un enchaînement fluide des mouvements.

Si vous le souhaitez, je peux ajouter un schéma explicatif du pipeline de transformation (position → rotation incrémentale → snap) ou ajouter une section « liens vers fonctions et fichiers » pointant précisément les fonctions dans `rubikCube.py` et `render3D`.
