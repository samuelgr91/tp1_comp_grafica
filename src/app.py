import glfw
import os
from src.vtk_loader import load_vtk
from src.renderer import Renderer

class App:
    def __init__(self, data_dir, n_term_str="064", initial_step=8, step_inc=8):
        self.window = None
        self.renderer = Renderer()
        
        # Data paths
        self.data_dir = data_dir
        self.n_term = n_term_str # "064", "128", "256"
        
        # State
        self.current_step = initial_step
        self.step_increment = step_inc
        self.max_step = int(n_term_str) # usually goes up to Nterm
        self.min_step = initial_step
        
        self.model = None
        self.needs_update = True
        
        # Animation state
        self.animation_playing = False  # Manual control only (use Space to play)
        self.animation_speed = 2.0  # Segments per second
        self.animation_timer = 0.0
        self.last_frame_time = None
        
        # View params
        self.view_params = {
            'zoom': 3.0,  # Start zoomed in for better visibility
            'pan_x': 0.0,
            'pan_y': 0.0,
            'rotation': 180.0 # Root at top, growing down
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
            # Model will show all segments by default (visible_count = None)
        else:
            print(f"File not found: {filepath}")

    def run(self):
        self.load_current_step()
        import time
        self.last_frame_time = time.time()
        
        while not glfw.window_should_close(self.window):
            # Update animation timer
            current_time = time.time()
            dt = current_time - self.last_frame_time
            self.last_frame_time = current_time
            
            # Progressive animation
            if self.animation_playing and self.model and self.model.visible_count is not None:
                self.animation_timer += dt * self.animation_speed
                if self.animation_timer >= 1.0:
                    self.animation_timer = 0.0
                    if self.model.visible_count < len(self.model.segments):
                        self.model.visible_count += 1
                    else:
                        # Reached end, load next step
                        if self.current_step < self.max_step:
                            self.current_step += self.step_increment
                            self.needs_update = True
                        else:
                            self.animation_playing = False  # Stop at end
            
            # Update logic
            if self.needs_update:
                self.load_current_step()
                self.needs_update = False

            # Render
            r, g, b = 0.0, 0.0, 0.0 # Black background
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
            if key == glfw.KEY_SPACE:
                # Toggle play/pause
                self.animation_playing = not self.animation_playing
                print(f"Animation: {'Playing' if self.animation_playing else 'Paused'}")
            elif key == glfw.KEY_RIGHT:
                # Speed up or skip forward
                if self.model and self.model.visible_count is not None:
                    self.model.visible_count = min(self.model.visible_count + 5, len(self.model.segments))
                else:
                    if self.current_step < self.max_step:
                        self.current_step += self.step_increment
                        self.needs_update = True
            elif key == glfw.KEY_LEFT:
                # Slow down or skip backward
                if self.model and self.model.visible_count is not None:
                    self.model.visible_count = max(self.model.visible_count - 5, 1)
                else:
                    if self.current_step > self.min_step:
                        self.current_step -= self.step_increment
                        self.needs_update = True
            elif key == glfw.KEY_UP:
                # Increase speed
                self.animation_speed *= 1.5
                print(f"Speed: {self.animation_speed:.1f} segments/sec")
            elif key == glfw.KEY_DOWN:
                # Decrease speed
                self.animation_speed /= 1.5
                print(f"Speed: {self.animation_speed:.1f} segments/sec")
            elif key == glfw.KEY_R:
                # Reset animation
                if self.model:
                    self.model.visible_count = 1
                    self.animation_playing = True
                print("Animation reset")
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
