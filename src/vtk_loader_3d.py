"""
Loader VTK para modelo 3D - TP2
Extrai do VTK (apenas estrutura topológica e geométrica):
- points: posições 3D (x,y,z)
- lines/cells: conectividade pai→filho
- radius: por segmento (CELL_DATA) → radius_point por vértice (média)
Constrói parent_of, children_of, detecta raiz, valida árvore.
"""
import os
import numpy as np
from src.model3d import Model3D


def load_vtk_3d(filepath: str) -> Model3D:
    """
    Parse VTK ASCII POLYDATA para árvore arterial 3D.
    Retorna Model3D com points, segments, radius_point e segment_list.
    """
    model = Model3D()


    with open(filepath, 'r') as f:
        lines = [l.strip() for l in f.readlines()]

    iterator = iter(lines)
    segment_radii = []

    try:
        while True:
            line = next(iterator)

            if line.upper().startswith("POINTS"):
                parts = line.split()
                num_points = int(parts[1])
                pts = []
                for _ in range(num_points):
                    p_line = next(iterator).split()
                    x, y, z = float(p_line[0]), float(p_line[1]), float(p_line[2])
                    pts.append([x, y, z])
                model.points = np.array(pts, dtype=np.float64)

            elif line.upper().startswith("LINES"):
                parts = line.split()
                num_lines = int(parts[1])
                for _ in range(num_lines):
                    l_line = next(iterator).split()
                    if l_line[0] == '2':
                        p1 = int(l_line[1])
                        p2 = int(l_line[2])
                        model.segments.append((p1, p2))

            elif line.upper().startswith("CELL_DATA"):
                pass

            elif line.upper().startswith("SCALARS"):
                next(iterator)
                for _ in range(len(model.segments)):
                    val = float(next(iterator))
                    segment_radii.append(val)

    except StopIteration:
        pass
    except Exception as e:
        print(f"Error parsing VTK: {e}")
        return None

    # Compute radius_point: média dos raios dos segmentos que tocam cada ponto
    n = len(model.points)
    radius_sum = np.zeros(n)
    radius_count = np.zeros(n)

    for (i0, i1), r in zip(model.segments, segment_radii):
        radius_sum[i0] += r
        radius_count[i0] += 1
        radius_sum[i1] += r
        radius_count[i1] += 1

    model.radius_point = np.where(radius_count > 0, radius_sum / radius_count, 0.01)
    model.radius_point = np.maximum(model.radius_point, 0.001)

    model.compute_bounds()
    try:
        model.build_segment_list()
    except ValueError as e:
        print(f"Erro: {e}")
        return None

    return model
