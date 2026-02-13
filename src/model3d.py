"""
Modelo 3D para árvore arterial - TP2
Estrutura explícita: parent_of, children_of, root.
Validação: grafo acíclico, cada nó (exceto raiz) tem exatamente 1 pai.
"""
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional


@dataclass
class Segment:
    """Ramo da árvore: liga nó pai (i0) a nó filho (i1)."""
    id: int
    i0: int
    i1: int
    p0: np.ndarray
    p1: np.ndarray
    r0: float
    r1: float
    length: float
    dir: np.ndarray
    depth: int
    is_root_segment: bool
    is_leaf_segment: bool


class Model3D:
    def __init__(self):
        self.points: np.ndarray = np.zeros((0, 3))
        self.segments: List[Tuple[int, int]] = []
        self.radius_point: np.ndarray = np.zeros(0)
        self.segment_list: List[Segment] = []
        self.bounds: Optional[Tuple[float, float, float, float, float, float]] = None
        self.target: np.ndarray = np.zeros(3)
        self.max_depth: int = 0
        self.visible_count: Optional[int] = None

        self.parent_of: Dict[int, int] = {}
        self.children_of: Dict[int, List[int]] = {}
        self.root: int = 0
        self.is_valid_tree: bool = False

    def compute_bounds(self):
        if len(self.points) == 0:
            return
        min_vals = np.min(self.points, axis=0)
        max_vals = np.max(self.points, axis=0)
        self.bounds = (min_vals[0], max_vals[0], min_vals[1], max_vals[1], min_vals[2], max_vals[2])
        self.target = (min_vals + max_vals) / 2.0

    def _build_tree_structure(self) -> bool:
        """
        Constrói parent_of e children_of a partir das lines.
        Detecta raiz: nó que nunca aparece como filho.
        Valida: sem ciclos, cada nó (exceto raiz) tem exatamente 1 pai.
        """
        self.parent_of = {}
        self.children_of = {}
        all_children = set()
        parent_candidates = {}

        for i0, i1 in self.segments:
            all_children.add(i1)
            if i0 not in self.children_of:
                self.children_of[i0] = []
            self.children_of[i0].append(i1)
            if i1 in parent_candidates and parent_candidates[i1] != i0:
                return False
            parent_candidates[i1] = i0

        roots = [i0 for i0, _ in self.segments if i0 not in all_children]
        if len(roots) != 1:
            return False
        self.root = roots[0]
        self.parent_of = parent_candidates

        visited = {self.root}
        queue = [self.root]
        while queue:
            node = queue.pop(0)
            for child in self.children_of.get(node, []):
                if child in visited:
                    return False
                visited.add(child)
                queue.append(child)

        if len(visited) != len(all_children) + 1:
            return False
        self.is_valid_tree = True
        return True

    def _bfs_order(self) -> List[Tuple[int, int, int]]:
        """Retorna (seg_id, i0, i1) em ordem BFS: raiz → galhos → ramificações → folhas."""
        order = []
        queue = [self.root]
        seg_by_endpoints = {(i0, i1): sid for sid, (i0, i1) in enumerate(self.segments)}

        while queue:
            node = queue.pop(0)
            for child in self.children_of.get(node, []):
                seg_id = seg_by_endpoints.get((node, child), -1)
                if seg_id >= 0:
                    order.append((seg_id, node, child))
                queue.append(child)

        return order

    def build_segment_list(self):
        """Constrói segment_list em ordem topológica (BFS)."""
        if not self._build_tree_structure():
            raise ValueError("VTK não representa uma árvore válida (ciclos ou múltiplas raízes)")

        parents = set(self.children_of.keys())
        leaves = set()
        for i0, i1 in self.segments:
            if i1 not in parents:
                leaves.add(i1)

        order = self._bfs_order()
        depth_map = {}
        queue = [(self.root, 0)]
        while queue:
            node, d = queue.pop(0)
            for child in self.children_of.get(node, []):
                seg_id = next((sid for sid, i0, i1 in order if i0 == node and i1 == child), -1)
                if seg_id >= 0:
                    depth_map[seg_id] = d
                queue.append((child, d + 1))

        self.max_depth = max(depth_map.values(), default=0)
        self.segment_list = []

        for seg_id, i0, i1 in order:
            p0 = np.array(self.points[i0], dtype=np.float64)
            p1 = np.array(self.points[i1], dtype=np.float64)
            diff = p1 - p0
            length = float(np.linalg.norm(diff))
            dir_vec = diff / length if length > 1e-10 else np.array([1.0, 0.0, 0.0])
            r0 = float(self.radius_point[i0]) if i0 < len(self.radius_point) else 0.01
            r1 = float(self.radius_point[i1]) if i1 < len(self.radius_point) else 0.01
            is_root_seg = i0 == self.root
            is_leaf_seg = i1 in leaves
            self.segment_list.append(Segment(
                id=seg_id, i0=i0, i1=i1, p0=p0, p1=p1, r0=r0, r1=r1,
                length=length, dir=dir_vec, depth=depth_map.get(seg_id, 0),
                is_root_segment=is_root_seg, is_leaf_segment=is_leaf_seg
            ))
