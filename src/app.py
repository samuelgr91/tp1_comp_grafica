import glfw
import os
from src.vtk_loader import load_vtk
from src.renderer import Renderer

class App:
    def __init__(self, data_dir, n_term_str="064"):
        self.window = None
        self.renderer = Renderer()
        
        # Data paths
        self.data_dir = data_dir
        self.n_term = n_term_str # "064", "128", "256"
        
        # State
        self.current_step = 8
        self.step_increment = 8
        self.max_step = int(n_term_str) # usually goes up to Nterm
        self.min_step = 8
        
        self.model = None
        self.needs_update = True
        
        # View params
        self.view_params = {
            'zoom': 1.0,
            'pan_x': 0.0,
            'pan_y': 0.0,
            'rotation': 0.0
        }
        
        self.last_mouse_pos = (0, 0)
        self.mouse_dragging = False
        self.mouse_button = None # 0: left, 1: right, 2: middle

    def init_gl(self):
        if not glfw.init():
            return False

        self.window = glfw.create_window(800, 600, "TP1 - 2D Arterial Tree", None, None)
        if not self.window:
            glfw.terminate()
            return False

        glfw.make_context_current(self.window)
        glfw.set_key_callback(self.window, self.key_callback)
        glfw.set_mouse_button_callback(self.window, self.mouse_button_callback)
        glfw.set_cursor_pos_callback(self.window, self.cursor_pos_callback)
        glfw.set_scroll_callback(self.window, self.scroll_callback)
        glfw.set_window_size_callback(self.window, self.window_size_callback)
        
        return True

    def load_current_step(self):
        # Filename pattern: tree2D_Nterm0064_step0008.vtk
        # Note the padding in Nterm part and step part
        # Nterm seems to be 4 digits in filename inside Nterm_064 folder?
        # Let's check the filename again: tree2D_Nterm0064_step0064.vtk
        # Directory: TP1_2D/Nterm_064
        
        step_str = f"{self.current_step:04d}"
        nterm_padded = f"{int(self.n_term):04d}"
        filename = f"tree2D_Nterm{nterm_padded}_step{step_str}.vtk"
        filepath = os.path.join(self.data_dir, filename)
        
        if os.path.exists(filepath):
            print(f"Loading: {filepath}")
            self.model = load_vtk(filepath)
            if self.model:
                # Optional: auto-center on first load?
                pass
        else:
            print(f"File not found: {filepath}")

    def run(self):
        self.load_current_step()
        
        while not glfw.window_should_close(self.window):
            # Update logic
            if self.needs_update:
                self.load_current_step()
                self.needs_update = False

            # Render
            r, g, b = 0.1, 0.1, 0.12 # Dark background
            from OpenGL.GL import glClear, glClearColor, GL_COLOR_BUFFER_BIT
            glClearColor(r, g, b, 1.0)
            glClear(GL_COLOR_BUFFER_BIT)
            
            self.renderer.render(self.model, self.view_params)
            
            glfw.swap_buffers(self.window)
            glfw.poll_events()
            
        glfw.terminate()

    # Callbacks
    def key_callback(self, window, key, scancode, action, mods):
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_RIGHT:
                if self.current_step < self.max_step:
                    self.current_step += self.step_increment
                    self.needs_update = True
            elif key == glfw.KEY_LEFT:
                if self.current_step > self.min_step:
                    self.current_step -= self.step_increment
                    self.needs_update = True
            elif key == glfw.KEY_ESCAPE:
                glfw.set_window_should_close(window, True)

    def mouse_button_callback(self, window, button, action, mods):
        if action == glfw.PRESS:
            self.mouse_dragging = True
            self.mouse_button = button
            self.last_mouse_pos = glfw.get_cursor_pos(window)
        elif action == glfw.RELEASE:
            self.mouse_dragging = False
            self.mouse_button = None

    def cursor_pos_callback(self, window, xpos, ypos):
        if self.mouse_dragging:
            dx = xpos - self.last_mouse_pos[0]
            dy = ypos - self.last_mouse_pos[1]
            self.last_mouse_pos = (xpos, ypos)
            
            # Sensitivity factors
            pan_speed = 0.002 / self.view_params['zoom']
            rot_speed = 0.5
            
            if self.mouse_button == glfw.MOUSE_BUTTON_RIGHT or self.mouse_button == glfw.MOUSE_BUTTON_MIDDLE:
                # Pan: moving mouse right (positive dx) should move view left (pan_x decrease)??
                # Typically: dragging world. If I drag mouse right, I expect world to move right.
                # In renderer: translate(-pan_x, -pan_y).
                # So if pan_x decreases, -pan_x increases, world moves right.
                self.view_params['pan_x'] -= dx * pan_speed
                self.view_params['pan_y'] += dy * pan_speed # dy is usually down-positive in screen, but y is up-positive
                
            elif self.mouse_button == glfw.MOUSE_BUTTON_LEFT:
                # Rotate
                self.view_params['rotation'] += dx * rot_speed

    def scroll_callback(self, window, xoffset, yoffset):
        zoom_speed = 1.1
        if yoffset > 0:
            self.view_params['zoom'] *= zoom_speed
        else:
            self.view_params['zoom'] /= zoom_speed

    def window_size_callback(self, window, width, height):
        self.renderer.resize(width, height)
