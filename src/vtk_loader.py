import os
from src.model import Model2D

def load_vtk(filepath):
    """
    Parses a simple legacy ASCII VTK file for the arterial tree project.
    Expects POLYDATA with POINTS, LINES, and CELL_DATA (SCALARS).
    """
    model = Model2D()
    
    with open(filepath, 'r') as f:
        lines = [l.strip() for l in f.readlines()]
        
    iterator = iter(lines)
    
    try:
        while True:
            line = next(iterator)
            
            if line.startswith("POINTS"):
                parts = line.split()
                num_points = int(parts[1])
                # dtype = parts[2] # usually float
                
                for _ in range(num_points):
                    p_line = next(iterator).split()
                    x, y, z = float(p_line[0]), float(p_line[1]), float(p_line[2])
                    model.vertices.append((x, y, z))
                    
            elif line.startswith("LINES"):
                parts = line.split()
                num_lines = int(parts[1])
                # total_ints = int(parts[2])
                
                for _ in range(num_lines):
                    l_line = next(iterator).split()
                    # format: num_points p1 p2 ... (usually 2 p1 p2 for segments)
                    if l_line[0] == '2':
                        p1 = int(l_line[1])
                        p2 = int(l_line[2])
                        model.segments.append((p1, p2))
                        
            elif line.startswith("CELL_DATA"):
                # Usually followed by SCALARS
                pass
                
            elif line.startswith("SCALARS"):
                # e.g. SCALARS raio float
                # followed by LOOKUP_TABLE default
                next(iterator) # skip LOOKUP_TABLE line
                
                # Should match number of segments (cells)
                for _ in range(len(model.segments)):
                    val = float(next(iterator))
                    model.radii.append(val)
                    
    except StopIteration:
        pass
    except Exception as e:
        print(f"Error parsing VTK: {e}")
        return None

    model.compute_bounds()
    return model
