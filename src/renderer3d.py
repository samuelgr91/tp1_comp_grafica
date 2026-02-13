"""
Renderer 3D - TP2
Árvore simples: linhas 3D conectando raiz → galhos → ramificações.
Igual ao TP1, só que em 3D.
"""
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective, gluLookAt
import numpy as np
import math
from src.model3d import Model3D, Segment


def _gradient(t):
    """Azul (ramos finos) -> verde -> amarelo -> vermelho (raiz)."""
    t = max(0.0, min(1.0, t))
    if t < 0.33:
        s = t / 0.33
        return (0.0, s * 0.5, 0.5 + 0.5 * (1 - s))
    if t < 0.66:
        s = (t - 0.33) / 0.33
        return (s * 0.5, 0.5 + 0.5 * s, 0.5 * (1 - s))
    s = (t - 0.66) / 0.34
    return (0.5 + 0.5 * s, 1.0, 0.0)


class Renderer3D:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.min_radius = 0.0
        self.max_radius = 1.0

    def resize(self, width, height):
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)

    def render(self, model: Model3D, view_params: dict, opts: dict):
        if not model or not model.segment_list:
            return

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, self.width / max(self.height, 1), 0.01, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        target = view_params.get('target', model.target)
        dist = view_params['distance']
        yaw = math.radians(view_params['yaw'])
        pitch = math.radians(view_params['pitch'])
        eye = np.array([
            target[0] + dist * math.cos(pitch) * math.sin(yaw),
            target[1] + dist * math.sin(pitch),
            target[2] + dist * math.cos(pitch) * math.cos(yaw)
        ])
        gluLookAt(eye[0], eye[1], eye[2], target[0], target[1], target[2], 0, 1, 0)

        self.max_depth_val = model.max_depth
        if len(model.radius_point) > 0:
            self.min_radius = float(np.min(model.radius_point))
            self.max_radius = float(np.max(model.radius_point))

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        fixed_radius = opts.get('fixed_radius', False)
        fixed_val = opts.get('fixed_radius_val', 0.02)
        color_by = opts.get('color_by', 'depth')
        selected_id = opts.get('selected_segment_id', -1)
        visible_count = model.visible_count

        segs = model.segment_list[:visible_count] if visible_count else model.segment_list

        glDisable(GL_LIGHTING)
        for seg in segs:
            r_avg = fixed_val if fixed_radius else (seg.r0 + seg.r1) / 2.0
            thickness = (r_avg ** 1.2) * 80
            glLineWidth(max(1.0, thickness))
            if seg.id == selected_id:
                glColor3f(1.0, 1.0, 0.0)
            else:
                if color_by == 'depth':
                    t = 1.0 - seg.depth / max(self.max_depth_val, 1)
                else:
                    t = (r_avg - self.min_radius) / max(self.max_radius - self.min_radius, 1e-6)
                    t = max(0.0, min(1.0, t))
                r, g, b = _gradient(t)
                glColor3f(r, g, b)
            glBegin(GL_LINES)
            glVertex3f(seg.p0[0], seg.p0[1], seg.p0[2])
            glVertex3f(seg.p1[0], seg.p1[1], seg.p1[2])
            glEnd()

        glDisable(GL_LINE_SMOOTH)
        glDisable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)
