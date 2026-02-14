"""
Renderer 3D - TP2
Renderização de árvore arterial com GL_LINES (espessura por raio).
Suporta iluminação Flat/Gouraud, transparência, coloração por depth/radius.
"""
import math
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective, gluLookAt


class Renderer3D:
    def __init__(self):
        self.width = 800
        self.height = 600

    def resize(self, width, height):
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)

    def _depth_to_rgb(self, t):
        """Colormap depth: azul (raiz) -> verde -> amarelo -> vermelho (folhas)."""
        t = max(0.0, min(1.0, t))
        if t < 0.25:
            u = t / 0.25
            return (0.0, u, 1.0)
        elif t < 0.5:
            u = (t - 0.25) / 0.25
            return (0.0, 1.0, 1.0 - u)
        elif t < 0.75:
            u = (t - 0.5) / 0.25
            return (u, 1.0, 0.0)
        else:
            u = (t - 0.75) / 0.25
            return (1.0, 1.0 - u, 0.0)

    def _radius_to_rgb(self, r_avg, r_min, r_max):
        """Colormap radius: ramos finos (azul) -> grossos (vermelho)."""
        if r_max <= r_min:
            t = 0.5
        else:
            t = (r_avg - r_min) / (r_max - r_min)
        t = max(0.0, min(1.0, t))
        return self._depth_to_rgb(t)

    def _get_color(self, seg, color_by, depth_max, radius_min, radius_max, light_factor=1.0):
        """Cor baseada em depth ou radius, com fator de iluminação."""
        if color_by == 'depth':
            t = seg.depth / max(depth_max, 1)
            r, g, b = self._depth_to_rgb(1.0 - t)
        else:
            r_avg = (seg.r0 + seg.r1) / 2.0
            r, g, b = self._radius_to_rgb(r_avg, radius_min, radius_max)
        def clamp(x):
            return max(0.0, min(1.0, x))
        return (clamp(r * light_factor), clamp(g * light_factor), clamp(b * light_factor))

    def render(self, model, view_params, options=None):
        if not model or not model.segment_list:
            return
        opts = options or {}
        fixed_radius = opts.get('fixed_radius', False)
        shade_model = opts.get('shade_model', GL_SMOOTH)
        transparency = opts.get('transparency', False)
        color_by = opts.get('color_by', 'depth')
        selected_id = opts.get('selected_segment_id', -1)

        segments = model.segment_list
        if model.visible_count is not None:
            segments = model.segment_list[:model.visible_count]

        depth_max = model.max_depth
        radii = [(s.r0 + s.r1) / 2.0 for s in segments]
        radius_min = min(radii) if radii else 0.001
        radius_max = max(radii) if radii else 0.01

        light_dir = np.array([0.5, 1.0, 0.5], dtype=np.float64)
        light_dir = light_dir / np.linalg.norm(light_dir)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = self.width / max(self.height, 1)
        gluPerspective(45.0, aspect, 0.001, 10.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        t = view_params['target']
        d = view_params['distance']
        yaw = math.radians(view_params['yaw'])
        pitch = math.radians(view_params['pitch'])
        eye_x = t[0] + d * math.cos(pitch) * math.sin(yaw)
        eye_y = t[1] + d * math.sin(pitch)
        eye_z = t[2] + d * math.cos(pitch) * math.cos(yaw)
        gluLookAt(eye_x, eye_y, eye_z, t[0], t[1], t[2], 0.0, 1.0, 0.0)

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glShadeModel(shade_model)

        if transparency:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glEnable(GL_LINE_SMOOTH)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
            cam_pos = np.array([eye_x, eye_y, eye_z])
            segs_with_dist = []
            for seg in segments:
                mid = (seg.p0 + seg.p1) / 2.0
                dist = np.linalg.norm(mid - cam_pos)
                segs_with_dist.append((seg, dist))
            segs_with_dist.sort(key=lambda x: -x[1])
            segments = [s for s, _ in segs_with_dist]

        for seg in segments:
            r = 0.01 if fixed_radius else max(seg.r0, seg.r1, 0.002)
            line_width = max(1.0, r * 80.0)
            glLineWidth(line_width)

            dot = max(0.0, np.dot(seg.dir, light_dir))
            light_factor = 0.4 + 0.6 * dot
            base = self._get_color(seg, color_by, depth_max, radius_min, radius_max, 1.0)
            if seg.id == selected_id:
                c0 = c1 = (1.0, 0.8, 0.2)
            else:
                if shade_model == GL_SMOOTH:
                    k = 0.3 * (2.0 * dot - 1.0)
                    f0 = max(0.3, light_factor - k)
                    f1 = max(0.3, light_factor + k)
                    c0 = tuple(max(0, min(1, base[i] * f0)) for i in range(3))
                    c1 = tuple(max(0, min(1, base[i] * f1)) for i in range(3))
                else:
                    c0 = c1 = self._get_color(seg, color_by, depth_max, radius_min, radius_max, light_factor)
            a = 0.7 if transparency else 1.0
            glBegin(GL_LINES)
            if transparency:
                glColor4f(c0[0], c0[1], c0[2], a)
            else:
                glColor3f(*c0)
            glVertex3f(seg.p0[0], seg.p0[1], seg.p0[2])
            if c0 != c1:
                if transparency:
                    glColor4f(c1[0], c1[1], c1[2], a)
                else:
                    glColor3f(*c1)
            glVertex3f(seg.p1[0], seg.p1[1], seg.p1[2])
            glEnd()

        if transparency:
            glDisable(GL_BLEND)
            glDisable(GL_LINE_SMOOTH)
        glLineWidth(1.0)
