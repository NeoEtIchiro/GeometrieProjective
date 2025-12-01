import numpy as np

def apply_camera_sequences(camera, cfg):
    camseqs = cfg.get('camera', {}).get('sequences', [])
    for seq in camseqs:
        duration = float(seq.get('duration', 2.0))
        zoom = float(seq.get('zoom', camera.orbit_radius))
        vertical = float(seq.get('vertical', camera.orbit_vert_amp))
        delay = float(seq.get('delay', 0.0))
        # On anime le rayon (zoom) et l'amplitude verticale
        # On ne touche pas à orbit_active, juste à ses paramètres
        def make_anim(target_radius, target_vert, duration, delay):
            start_radius = camera.orbit_radius
            start_vert = camera.orbit_vert_amp
            def anim_fn(dt, elapsed, total):
                t = min(1.0, elapsed / total)
                camera.orbit_radius = (1-t)*start_radius + t*target_radius
                camera.orbit_vert_amp = (1-t)*start_vert + t*target_vert
            return {'duration': duration, 'delay': delay, 'elapsed': 0.0, 'fn': anim_fn}
        camera._pending_anims = getattr(camera, '_pending_anims', [])
        camera._pending_anims.append(make_anim(zoom, vertical, duration, delay))

class Camera:
    def __init__(self, position=[0.0, 0.0, 0.0], speed=3.0):
        self.position = np.array(position, dtype=float)
        self.speed = float(speed)

        self.yaw = 0.0
        self.pitch = 0.0
        self.rot_speed = 1.5  # rad/s

        self.animations = []

        # Orbit params (disabled par défaut)
        self.orbit_active = False
        self.orbit_center = np.array([0.0, 0.0, 0.0], dtype=float)
        self.orbit_radius = 15.0
        self.orbit_ang_speed = 0.5       # rad/s
        self.orbit_vert_amp = 2.0
        self.orbit_vert_speed = 0.8      # rad/s
        self._orbit_elapsed = 0.0

    def start_orbit(self, center=[0.0,0.0,0.0], radius=15.0, ang_speed=0.5, vert_amp=2.0, vert_speed=0.8):
        self.orbit_active = True
        self.orbit_center = np.array(center, dtype=float)
        self.orbit_radius = float(radius)
        self.orbit_ang_speed = float(ang_speed)
        self.orbit_vert_amp = float(vert_amp)
        self.orbit_vert_speed = float(vert_speed)
        self._orbit_elapsed = 0.0

    def stop_orbit(self):
        self.orbit_active = False

    def enqueue_move(self, delta, duration, delay=0.0):
        """Enfile un mouvement relatif (delta) qui s'exécute sur 'duration' secondes après 'delay'."""
        anim = {
            'delta': np.array(delta, dtype=float),
            'duration': float(duration),
            'elapsed': 0.0,
            'last_progress': 0.0,
            'delay': float(delay)
        }
        self.animations.append(anim)

    def clear_animations(self):
        self.animations.clear()

    def _step_animations(self, dt):
        if not self.animations:
            return

        remaining = []
        for anim in self.animations:
            if anim['delay'] > 1e-12:
                # décrémente le délai sans appliquer de mouvement tant que delay > 0
                anim['delay'] -= dt
                if anim['delay'] > 0:
                    remaining.append(anim)
                    continue
                # delay consommé, la partie "elapsed" commence maintenant (on ne consomme pas dt supplémentaire)
            # avance l'animation
            anim['elapsed'] += dt
            dur = max(anim['duration'], 1e-12)
            progress = min(1.0, anim['elapsed'] / dur)
            last = anim['last_progress']
            # incrément relatif à appliquer ce frame
            inc = (progress - last) * anim['delta']
            self.position += inc
            anim['last_progress'] = progress
            if progress < 1.0:
                remaining.append(anim)
            # sinon animation terminée -> ne la remet pas dans remaining (elle est consommée)
        self.animations = remaining

    def update(self, dt):
        # Si orbit activée, calcule la position orbitale de base (centre + offset).
        if self.orbit_active:
            self._orbit_elapsed += dt
            theta = self.orbit_ang_speed * self._orbit_elapsed
            vtheta = self.orbit_vert_speed * self._orbit_elapsed
            ox = self.orbit_radius * np.sin(theta)
            oz = self.orbit_radius * np.cos(theta)
            oy = self.orbit_vert_amp * np.sin(vtheta)
            self.position = self.orbit_center + np.array([ox, oy, oz], dtype=float)

        # --- Ajout : gestion des animations de paramètres d'orbite ---
        if hasattr(self, '_pending_anims'):
            still_pending = []
            for anim in self._pending_anims:
                if anim['delay'] > 0:
                    anim['delay'] -= dt
                    still_pending.append(anim)
                    continue
                anim['elapsed'] += dt
                anim['fn'](dt, anim['elapsed'], anim['duration'])
                if anim['elapsed'] < anim['duration']:
                    still_pending.append(anim)
            self._pending_anims = still_pending

        # --- Caméra regarde toujours le centre du cube ---
        direction = -self.position
        self.yaw = np.arctan2(direction[0], direction[2])
        self.pitch = -np.arctan2(direction[1], np.sqrt(direction[0]**2 + direction[2]**2))

        self._step_animations(dt)