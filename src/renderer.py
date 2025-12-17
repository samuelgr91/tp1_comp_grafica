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
        
        # Jet/Rainbow Colormap (Blue -> Cyan -> Green -> Yellow -> Red)
        # 4 segments: 0-0.25, 0.25-0.5, 0.5-0.75, 0.75-1.0
        
        r, g, b = 0.0, 0.0, 0.0
        
        if t < 0.25:
            # Blue (0,0,1) -> Cyan (0,1,1)
            # t goes 0 -> 0.25. Normalize to 0 -> 1
            local_t = t / 0.25
            r, g, b = 0.0, local_t, 1.0
        elif t < 0.5:
            # Cyan (0,1,1) -> Green (0,1,0)
            local_t = (t - 0.25) / 0.25
            r, g, b = 0.0, 1.0, 1.0 - local_t
        elif t < 0.75:
            # Green (0,1,0) -> Yellow (1,1,0)
            local_t = (t - 0.5) / 0.25
            r, g, b = local_t, 1.0, 0.0
        else:
            # Yellow (1,1,0) -> Red (1,0,0)
            local_t = (t - 0.75) / 0.25
            r, g, b = 1.0, 1.0 - local_t, 0.0
            
        return (r, g, b)

    def draw_circle(self, x, y, radius, color):
        glColor3f(*color)
        num_segments = 8 # Optimized for performance (was 12)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(x, y) # center
        for i in range(num_segments + 1):
            theta = 2.0 * math.pi * float(i) / float(num_segments)
            dx = radius * math.cos(theta)
            dy = radius * math.sin(theta)
            glVertex2f(x + dx, y + dy)
        glEnd()

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

        for i, (p1_idx, p2_idx) in enumerate(model.segments):
            x1, y1, z1 = model.vertices[p1_idx]
            x2, y2, z2 = model.vertices[p2_idx]
            r = model.radii[i]
            
            # Color
            c = self.get_color(r)
            glColor3f(*c)

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
            
            rx = nx * r
            ry = ny * r
            
            glBegin(GL_QUADS)
            glVertex2f(x1 + rx, y1 + ry)
            glVertex2f(x2 + rx, y2 + ry)
            glVertex2f(x2 - rx, y2 - ry)
            glVertex2f(x1 - rx, y1 - ry)
            glEnd()
            
            # Draw rounded joints (circles) at endpoints
            # Drawing at both ends helps smooth connections
            self.draw_circle(x1, y1, r, c)
            self.draw_circle(x2, y2, r, c)
