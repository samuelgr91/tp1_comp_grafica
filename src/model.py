import numpy as np

class Model2D:
    def __init__(self):
        self.vertices = []  # List of [x, y, z] (z=0 for 2D)
        self.segments = []  # List of [start_index, end_index]
        self.radii = []     # List of float radius per segment
        self.bounds = None  # (min_x, max_x, min_y, max_y)
        self.visible_count = None  # None = show all, int = show first N segments

    def compute_bounds(self):
        if not self.vertices:
            return
        
        verts = np.array(self.vertices)
        min_vals = np.min(verts, axis=0)
        max_vals = np.max(verts, axis=0)
        
        # simple margin
        self.bounds = (min_vals[0], max_vals[0], min_vals[1], max_vals[1])
        
    def get_center(self):
        if not self.bounds:
            self.compute_bounds()
        
        cx = (self.bounds[0] + self.bounds[1]) / 2.0
        cy = (self.bounds[2] + self.bounds[3]) / 2.0
        return (cx, cy)
