from OpenGL.GL import *
import math

class Renderer:
    def __init__(self):
        self.width = 800
        self.height = 600
        # Simple colormap (Blue to Red)
        self.min_radius = 0.0
        self.max_radius = 1.0

    def resize(self, width, height):
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)

    def get_color(self, radius):
        # Normalize radius 0..1 for color
        if self.max_radius == self.min_radius:
            t = 0.5
        else:
            t = (radius - self.min_radius) / (self.max_radius - self.min_radius)
        t = max(0.0, min(1.0, t))
        
        # Blue (0,0,1) to Red (1,0,0) pipeline
        # Maybe Green in middle? 
        # Low -> Blue, High -> Red
        return (t, 0.0, 1.0 - t)

    def render(self, model, view_params):
        if not model:
            return

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        # Ortho projection centered on (0,0) locally, zoomed by scale, panned by translation
        # Aspect ratio handling:
        aspect = self.width / self.height
        
        zoom = view_params['zoom']
        pan_x = view_params['pan_x']
        pan_y = view_params['pan_y']
        
        # Visible window size in world units
        # If zoom=1, window is maybe 2.0x2.0 (from -1 to 1)
        w_size = 2.0 / zoom
        h_size = 2.0 / zoom
        
        if aspect > 1:
            w_size *= aspect
        else:
            h_size /= aspect

        glOrtho(-w_size/2 - pan_x, w_size/2 - pan_x, 
                -h_size/2 - pan_y, h_size/2 - pan_y, 
                -1.0, 1.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Rotate around center
        glRotatef(view_params['rotation'], 0, 0, 1)

        # Update min/max radii for coloring if needed (do once or dynamic?)
        # For performance, we assume standard ranges or calc once.
        if model.radii:
            self.max_radius = max(model.radii)
            self.min_radius = min(model.radii)

        glBegin(GL_QUADS)
        
        for i, (p1_idx, p2_idx) in enumerate(model.segments):
            x1, y1, z1 = model.vertices[p1_idx]
            x2, y2, z2 = model.vertices[p2_idx]
            r = model.radii[i]
            
            # Draw segment as quad
            dx = x2 - x1
            dy = y2 - y1
            length = math.sqrt(dx*dx + dy*dy)
            
            if length == 0:
                continue
                
            ux = dx / length
            uy = dy / length
            
            # Perpendicular vector
            nx = -uy
            ny = ux
            
            # Thickness scaled 
            # Note: r is radius, so full width is 2*r.
            # But visually, we might need to scale it if units are tiny.
            # Based on image, radii are ~0.02 vs coords ~0.05. It's comparable.
            
            rx = nx * r
            ry = ny * r
            
            # Color
            c = self.get_color(r)
            glColor3f(*c)
            
            glVertex2f(x1 + rx, y1 + ry)
            glVertex2f(x2 + rx, y2 + ry)
            glVertex2f(x2 - rx, y2 - ry)
            glVertex2f(x1 - rx, y1 - ry)
            
        glEnd()
