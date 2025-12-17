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
        
        # Enhanced Green Gradient with stronger contrast
        # Thin branches (far from root): Very dark green, almost invisible
        # Thick branches (root): Bright neon green
        
        # Use power function for non-linear brightness
        brightness = t ** 0.7  # Makes thin branches darker
        
        r = 0.0 + 0.3 * brightness  # More red for neon effect
        g = 0.15 + 0.85 * brightness  # Darker base, brighter peak
        b = 0.0 + 0.3 * brightness  # More blue for neon effect
            
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
        aspect = self.width / max(self.height, 1)  # Prevent division by zero
        
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

        # Determine how many segments to render (for animation)
        segments_to_render = model.segments
        radii_to_render = model.radii
        if model.visible_count is not None:
            segments_to_render = model.segments[:model.visible_count]
            radii_to_render = model.radii[:model.visible_count]

        # Enable line smoothing for rounder appearance
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        for i, (p1_idx, p2_idx) in enumerate(segments_to_render):
            x1, y1, z1 = model.vertices[p1_idx]
            x2, y2, z2 = model.vertices[p2_idx]
            r = radii_to_render[i]
            
            # Color
            c = self.get_color(r)
            glColor3f(*c)

            # Draw segment as line with thickness
            # Enhanced scaling: thin branches very thin, thick branches very thick
            thickness = (r ** 1.2) * 250  # Non-linear scaling for more contrast
            glLineWidth(max(0.5, thickness))  # Minimum 0.5 to keep thin branches visible
            glBegin(GL_LINES)
            glVertex2f(x1, y1)
            glVertex2f(x2, y2)
            glEnd()
        
        # Disable smoothing after rendering
        glDisable(GL_LINE_SMOOTH)
        glDisable(GL_BLEND)
