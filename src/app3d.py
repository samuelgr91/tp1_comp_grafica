"""
App 3D - TP2
Mesma estrutura do TP1: navegação por steps, setas, animação progressiva.
Usa dataset TP2_3D.
"""
import glfw
import os
import time
import math
import numpy as np
from OpenGL.GL import glClearColor, glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_SMOOTH
from src.vtk_loader_3d import load_vtk_3d
from src.renderer3d import Renderer3D
from src.picking import pick_segment
from src.dataset_utils import auto_detect_dataset


class App3D:
    def __init__(self, data_dir, n_term_str="128", initial_step=16, step_inc=16):
        self.window = None
        self.renderer = Renderer3D()
        self.data_dir = data_dir
        self.n_term = n_term_str
        self.current_step = initial_step
        self.step_increment = step_inc
        self.max_step = int(n_term_str)
        self.min_step = initial_step
        self.model = None
        self.needs_update = True

        # Animação (igual TP1)
        self.animation_playing = False
        self.animation_speed = 2.0
        self.animation_timer = 0.0
        self.last_frame_time = None

        # Câmera: orbit (esquerdo) + pan (direito ou Shift+esquerdo)
        self.view_params = {
            'yaw': 45.0,
            'pitch': 25.0,
            'distance': 0.15,
            'target': [0.0, 0.0, 0.0]
        }

        # Opções de render (TP2)
        self.fixed_radius = False
        self.shade_model = GL_SMOOTH
        self.transparency = False
        self.color_by = 'depth'
        self.selected_segment_id = -1

        self.last_mouse_pos = (0.0, 0.0)
        self.mouse_dragging = False
        self.mouse_button = None
        self.mouse_mods = 0
        self.mouse_dragged = False

    def init_gl(self):
        if not glfw.init():
            return False
        self.window = glfw.create_window(800, 600, "TP2 - 3D Arterial Tree", None, None)
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
        """Carrega arquivo do step atual (igual TP1, mas tree3D)."""
        step_str = f"{self.current_step:04d}"
        nterm_padded = f"{int(self.n_term):04d}"
        filename = f"tree3D_Nterm{nterm_padded}_step{step_str}.vtk"
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            print(f"Loading: {filepath}")
            self.model = load_vtk_3d(filepath)
            if self.model and self.model.is_valid_tree:
                bifurc = sum(1 for c in self.model.children_of.values() if len(c) >= 2)
                print(f"  Árvore: raiz={self.model.root}, {len(self.model.segment_list)} ramos, "
                      f"{bifurc} bifurcações, depth_max={self.model.max_depth}")
                self.model.visible_count = None
                self.view_params['target'] = self.model.target.tolist()
                if self.model.bounds:
                    ext = np.array([
                        self.model.bounds[1] - self.model.bounds[0],
                        self.model.bounds[3] - self.model.bounds[2],
                        self.model.bounds[5] - self.model.bounds[4]
                    ])
                    self.view_params['distance'] = max(0.05, float(np.linalg.norm(ext)) * 1.2)
        else:
            print(f"File not found: {filepath}")

    def run(self):
        self.load_current_step()
        self.last_frame_time = time.time()

        while not glfw.window_should_close(self.window):
            dt = time.time() - self.last_frame_time
            self.last_frame_time = time.time()

            # Animação progressiva (igual TP1)
            if self.animation_playing and self.model and self.model.visible_count is not None:
                self.animation_timer += dt * self.animation_speed
                if self.animation_timer >= 1.0:
                    self.animation_timer = 0.0
                    if self.model.visible_count < len(self.model.segment_list):
                        self.model.visible_count += 1
                    else:
                        if self.current_step < self.max_step:
                            self.current_step += self.step_increment
                            self.needs_update = True
                        else:
                            self.animation_playing = False

            if self.needs_update:
                self.load_current_step()
                self.needs_update = False

            glClearColor(0.08, 0.08, 0.12, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.renderer.render(self.model, self.view_params, {
                'fixed_radius': self.fixed_radius,
                'shade_model': self.shade_model,
                'transparency': self.transparency,
                'color_by': self.color_by,
                'selected_segment_id': self.selected_segment_id
            })
            glfw.swap_buffers(self.window)
            glfw.poll_events()

        glfw.terminate()

    def key_callback(self, window, key, scancode, action, mods):
        if action != glfw.PRESS and action != glfw.REPEAT:
            return
        from OpenGL.GL import GL_FLAT
        if key == glfw.KEY_SPACE:
            self.animation_playing = not self.animation_playing
        elif key == glfw.KEY_RIGHT:
            if self.model and self.model.visible_count is not None:
                self.model.visible_count = min(self.model.visible_count + 5, len(self.model.segment_list))
            else:
                if self.current_step < self.max_step:
                    self.current_step += self.step_increment
                    self.needs_update = True
        elif key == glfw.KEY_LEFT:
            if self.model and self.model.visible_count is not None:
                self.model.visible_count = max(self.model.visible_count - 5, 1)
            else:
                if self.current_step > self.min_step:
                    self.current_step -= self.step_increment
                    self.needs_update = True
        elif key == glfw.KEY_UP:
            self.animation_speed *= 1.5
        elif key == glfw.KEY_DOWN:
            self.animation_speed /= 1.5
        elif key == glfw.KEY_R:
            self.fixed_radius = not self.fixed_radius
        elif key == glfw.KEY_1:
            self.shade_model = GL_FLAT
        elif key == glfw.KEY_2:
            self.shade_model = GL_SMOOTH
        elif key == glfw.KEY_T:
            self.transparency = not self.transparency
        elif key == glfw.KEY_C:
            self.color_by = 'radius' if self.color_by == 'depth' else 'depth'
        elif key == glfw.KEY_0 and self.model:
            self.model.visible_count = 1
            self.animation_playing = True
        elif key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)

    def mouse_button_callback(self, window, button, action, mods):
        if action == glfw.PRESS:
            self.mouse_dragging = True
            self.mouse_button = button
            self.mouse_mods = mods
            self.mouse_dragged = False
            self.last_mouse_pos = glfw.get_cursor_pos(window)
        elif action == glfw.RELEASE:
            if button == glfw.MOUSE_BUTTON_LEFT and self.model and not self.mouse_dragged:
                x, y = glfw.get_cursor_pos(window)
                _, h = glfw.get_framebuffer_size(window)
                self.selected_segment_id = pick_segment(self.model, x, y, h)
                if self.selected_segment_id >= 0:
                    seg = next((s for s in self.model.segment_list if s.id == self.selected_segment_id), None)
                    if seg:
                        print(f"[HUD] id={seg.id} length={seg.length:.4f} r0={seg.r0:.4f} r1={seg.r1:.4f} depth={seg.depth}")
            self.mouse_dragging = False
            self.mouse_button = None

    def cursor_pos_callback(self, window, xpos, ypos):
        if not self.mouse_dragging:
            return
        dx = xpos - self.last_mouse_pos[0]
        dy = ypos - self.last_mouse_pos[1]
        self.last_mouse_pos = (xpos, ypos)
        if abs(dx) > 2 or abs(dy) > 2:
            self.mouse_dragged = True

        is_pan = (self.mouse_button == glfw.MOUSE_BUTTON_RIGHT or
                  (self.mouse_button == glfw.MOUSE_BUTTON_LEFT and (self.mouse_mods & glfw.MOD_SHIFT)))

        if is_pan:
            t = np.array(self.view_params['target'])
            d = self.view_params['distance']
            yaw = math.radians(self.view_params['yaw'])
            pitch = math.radians(self.view_params['pitch'])
            view = np.array([
                -math.cos(pitch) * math.sin(yaw),
                -math.sin(pitch),
                -math.cos(pitch) * math.cos(yaw)
            ])
            right = np.cross(view, [0, 1, 0])
            n = np.linalg.norm(right)
            if n > 1e-6:
                right = right / n
            up = np.cross(right, view)
            n = np.linalg.norm(up)
            if n > 1e-6:
                up = up / n
            pan_speed = d * 0.002
            t = t + dx * pan_speed * right - dy * pan_speed * up
            self.view_params['target'] = t.tolist()
        else:
            sens = 0.6
            self.view_params['yaw'] -= dx * sens
            self.view_params['pitch'] = max(-89, min(89, self.view_params['pitch'] + dy * sens))

    def scroll_callback(self, window, xoffset, yoffset):
        s = 1.08 if yoffset > 0 else 1.0 / 1.08
        self.view_params['distance'] = max(0.02, min(2.0, self.view_params['distance'] / s))

    def window_size_callback(self, window, width, height):
        self.renderer.resize(width, height)
