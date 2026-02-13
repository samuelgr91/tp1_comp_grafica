"""
Picking por ray cast - TP2
Ray a partir do mouse, teste contra cápsulas (segmentos).
"""
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import gluUnProject


def get_ray_from_mouse(mouse_x: float, mouse_y: float, viewport_height: int):
    """Retorna (ray_origin, ray_dir) em coordenadas de mundo."""
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)
    viewport = glGetIntegerv(GL_VIEWPORT)
    # mouse_y está em coordenadas de janela (y para cima); OpenGL viewport y para baixo
    win_y = viewport[3] - mouse_y
    ray_start = gluUnProject(mouse_x, win_y, 0.0, modelview, projection, viewport)
    ray_end = gluUnProject(mouse_x, win_y, 1.0, modelview, projection, viewport)
    ray_start = np.array(ray_start)
    ray_end = np.array(ray_end)
    ray_dir = ray_end - ray_start
    n = np.linalg.norm(ray_dir)
    if n < 1e-10:
        return ray_start, np.array([0.0, 0.0, 1.0])
    ray_dir = ray_dir / n
    return ray_start, ray_dir


def _closest_point_on_segment(p: np.ndarray, a: np.ndarray, b: np.ndarray) -> tuple:
    """Ponto mais próximo em segmento [a,b] ao ponto p. Retorna (point, t) onde t em [0,1]."""
    ab = b - a
    ap = p - a
    t = np.dot(ap, ab) / (np.dot(ab, ab) + 1e-20)
    t = max(0.0, min(1.0, t))
    closest = a + t * ab
    return closest, t


def _ray_segment_distance(ray_origin: np.ndarray, ray_dir: np.ndarray,
                          seg_p0: np.ndarray, seg_p1: np.ndarray) -> tuple:
    """
    Distância entre raio e segmento. Retorna (distance, t_ray) onde t_ray é o parâmetro
    ao longo do raio do ponto mais próximo.
    """
    # Ponto mais próximo no raio ao segmento: resolver para t
    # Raio: O + t*D
    # Segmento: A + s*(B-A), s in [0,1]
    # Queremos minimizar |(O+tD) - (A+s(B-A))|^2
    a = seg_p0
    b = seg_p1
    ab = b - a
    ao = ray_origin - a
    d = ray_dir

    # Sistema: (O+tD - A - s*AB) perpendicular a D e AB
    # (O+tD - A - s*AB)·D = 0  =>  t - s*(AB·D) = -AO·D
    # (O+tD - A - s*AB)·AB = 0  =>  t*(D·AB) - s*|AB|^2 = -AO·AB
    denom = np.dot(d, d) * np.dot(ab, ab) - np.dot(d, ab) ** 2
    if abs(denom) < 1e-20:
        # Raio paralelo ao segmento
        closest_on_seg, _ = _closest_point_on_segment(ray_origin, a, b)
        diff = ray_origin - closest_on_seg
        dist = np.linalg.norm(diff)
        t_ray = 0.0
        return dist, t_ray

    t_ray = (np.dot(ab, ab) * np.dot(-ao, d) + np.dot(d, ab) * np.dot(ao, ab)) / denom
    s = (np.dot(d, d) * np.dot(ao, ab) + np.dot(d, ab) * np.dot(-ao, d)) / denom
    s = max(0.0, min(1.0, s))
    t_ray = max(0.0, t_ray)

    point_on_ray = ray_origin + t_ray * d
    point_on_seg = a + s * ab
    dist = np.linalg.norm(point_on_ray - point_on_seg)
    return dist, t_ray


def pick_segment(model, mouse_x: float, mouse_y: float, viewport_height: int) -> int:
    """
    Retorna o id do segmento selecionado ou -1.
    Aproximação por cápsula: dist < max(r0, r1) -> hit.
    Escolhe o de menor t (mais próximo da câmera).
    """
    ray_origin, ray_dir = get_ray_from_mouse(mouse_x, mouse_y, viewport_height)

    best_id = -1
    best_t = float('inf')

    for seg in model.segment_list:
        dist, t_ray = _ray_segment_distance(ray_origin, ray_dir, seg.p0, seg.p1)
        radius = max(seg.r0, seg.r1, 0.005)
        if dist < radius and t_ray < best_t:
            best_t = t_ray
            best_id = seg.id

    return best_id
