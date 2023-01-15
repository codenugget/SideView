from OpenGL.GL import *

import glfw
import imgui
import math
import numpy as np
import pyrr

import color_shader
import Converter as conv
import gfx
import ObjParse as op

class ConvertModel(gfx.Base):
    def __init__(self):
        super().__init__()
        self.title = "Side View"
        self.desired_width = 1024
        self.desired_height = 768

        self.shader = -1
        self.pos_attr = -1
        self.uv_attr = -1
        self.nrm_attr = -1
        self.proj_uform = -1
        self.model_uform = -1
        self.col_uform = -1
        self.bkg_uform = -1
        self.fresnel_uform = -1
        self.ui_clear_color = .0, .0, .3, 1.
        self.ui_shader_color = 1.0, 1.0, 1.0, 1.0
        self.ui_bias = 0.0
        self.ui_scale = 1.0
        self.ui_power = 2.5
        self.ui_bkg_term = 0.3
        self.fresnel = [self.ui_bias, self.ui_scale, self.ui_power, self.ui_bkg_term]
        self.ui_display_menu = False
        self.num_vertices = 0
        self.geom = None
        self.text = str()
        self.ident = np.zeros([1, 16], dtype = np.float32).flatten()
        self.ident[0] = np.float32(1.0)
        self.ident[5] = np.float32(1.0)
        self.ident[10] = np.float32(1.0)
        self.ident[15] = np.float32(1.0)
        self.Mproj = np.copy(self.ident)
        self.Mmodel = np.copy(self.ident)

        self.camera_distance = 5.0
        self.camera_angle_up = 0.
        self.camera_angle_side = 0.
        self.camera_eye = self.calc_eye()
        #self.camera_eye = np.array([4, 3, 3])
        self.camera_lookat = np.array([0, 0, 0])
        #self.camera_lookat = np.array([1, 1, 0])
        self.camera_up = np.array([0, 1, 0])
        self.camera_fovy = 45.0
        self.camera_z_near = 0.1
        self.camera_z_far = 100.0
        self.aspect = 1.0
        self.rot_mode = False
        self.zoom_mode = False
        self.mouse_x = 0.
        self.mouse_y = 0.
        self.load_settings() # load settings file if it exists

    def load_settings(self):
        try:
            lines = []
            with open("Settings.txt", "r") as fp:
                lines = fp.readlines()
                fp.close()
            if len(lines) != 12:
                raise Exception("Too few lines")
            r, g, b, a = float(lines[0]), float(lines[1]), float(lines[2]), float(lines[3])
            self.ui_clear_color = [r, g, b, a]
            r, g, b, a = float(lines[4]), float(lines[5]), float(lines[6]), float(lines[7])
            self.ui_shader_color = [r, g, b, a]

            r, g, b, a = float(lines[8]), float(lines[9]), float(lines[10]), float(lines[11])
            self.fresnel = [r, g, b, a]
            self.ui_bias = r
            self.ui_scale = g
            self.ui_power = b
            self.ui_bkg_term = a
        except Exception as e:
            print(e)
            pass

    def save_settings(self):
        with open("Settings.txt", "w") as fp:
            fp.write(f"{self.ui_clear_color[0]}\n")
            fp.write(f"{self.ui_clear_color[1]}\n")
            fp.write(f"{self.ui_clear_color[2]}\n")
            fp.write(f"{self.ui_clear_color[3]}\n")

            fp.write(f"{self.ui_shader_color[0]}\n")
            fp.write(f"{self.ui_shader_color[1]}\n")
            fp.write(f"{self.ui_shader_color[2]}\n")
            fp.write(f"{self.ui_shader_color[3]}\n")

            fp.write(f"{self.fresnel[0]}\n")
            fp.write(f"{self.fresnel[1]}\n")
            fp.write(f"{self.fresnel[2]}\n")
            fp.write(f"{self.fresnel[3]}\n")
            fp.close()

    def calc_trf(self):
        pi = 3.14159265
        up_rad = self.camera_angle_up * pi / 180.0
        side_rad = self.camera_angle_side * pi / 180.0

        M1 = pyrr.matrix33.create_from_axis_rotation(pyrr.Vector3([0.,1.,0.]), up_rad)
        M2 = pyrr.matrix33.create_from_axis_rotation(pyrr.Vector3([1.,0.,0.]), side_rad)
        return pyrr.matrix33.multiply(M1, M2)

    def calc_eye(self):
        r = self.camera_distance
        M = self.calc_trf()
        eye = M @ pyrr.Vector3([0.,0.,r])
        up = M @ pyrr.Vector3([0.,1.,0.])
        return np.array(eye), np.array(up)

    def setup(self, window, w, h):
        if not super().setup(window, w, h):
            return False

        self.aspect = w / h
        model_filename = 'fake_tumour.obj'
        scene = None
        try:
            scene = op.ObjParse(filename=model_filename, verbose=False)
        except FileNotFoundError as e:
            print(str(e))
            print(f"ERROR: Unable to find {model_filename}")
            return False
        except Exception as e:
            print(str(e))
            print(f"ERROR: Unable to parse {model_filename}")
            return False

        self.shader, self.pos_attr, self.uv_attr, self.nrm_attr, self.proj_uform, self.model_uform, self.col_uform, self.bkg_uform, self.fresnel_uform = color_shader.create()

        self.geom = conv.convert_tris(scene)
        # convert positions to 32bit float
        self.geom.vertex_data = np.array(self.geom.vertex_data, dtype = np.float32)

        self.num_vertices = self.geom.count_verts()
        vertex_attrib_bytes = self.geom.count_attrib_bytes()
        num_array_bytes = self.geom.count_bytes()

        # Create buffer object
        self.vertex_buffer_object = glGenBuffers(1) 

        # Bind the buffer and setup the attrib arrays

        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer_object)
        glBufferData(GL_ARRAY_BUFFER, num_array_bytes, self.geom.vertex_data, GL_STATIC_DRAW)

        glVertexAttribPointer(self.pos_attr, 3, GL_FLOAT, GL_FALSE, vertex_attrib_bytes, None)
        glEnableVertexAttribArray(self.pos_attr)
        skip_bytes = 3 * 4

        if self.geom.has_uv:
            glVertexAttribPointer(self.uv_attr, 2, GL_FLOAT, GL_FALSE, vertex_attrib_bytes, ctypes.c_void_p(skip_bytes))
            glEnableVertexAttribArray(self.uv_attr)
            skip_bytes += 2 * 4

        if self.geom.has_nrm:
            glVertexAttribPointer(self.nrm_attr, 3, GL_FLOAT, GL_FALSE, vertex_attrib_bytes, ctypes.c_void_p(skip_bytes))
            glEnableVertexAttribArray(self.nrm_attr)
            skip_bytes += 3 * 4

        glUseProgram(self.shader) # This activates the shader
        #glUseProgram(0) # This can be used to disable the shader (when desired)

        # enable rendering to be transparent
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # enable depth test
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        glEnable(GL_CULL_FACE)
        return True


    def finish(self):
        # cleanup here
        glDeleteBuffers(1, [self.vertex_buffer_object])
        super().finish() # call this at the last step here


    def key(self, key, scancode, action, mods):
        #print(f"key={key}  scancode={scancode}  action={action}  mods={mods}")
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            self.ui_display_menu = not self.ui_display_menu

    def mouse_enter(self, enter):
        pass #print(f"{enter}")

    def mouse_move(self, xpos, ypos):
        scale_dx = 1.
        scale_dy = 1.
        if self.rot_mode:
            dx = xpos - self.mouse_x
            dy = ypos - self.mouse_y
            self.camera_angle_up = self.camera_angle_up + dx * scale_dx
            self.camera_angle_side = self.camera_angle_side + dy * scale_dy
            if (self.camera_angle_side > 90):
                self.camera_angle_side = 90
            if (self.camera_angle_side < -90):
                self.camera_angle_side = -90
        if self.zoom_mode:
            dy = ypos - self.mouse_y
            self.camera_distance = self.camera_distance + dy * 0.01
            if self.camera_distance < 1:
                self.camera_distance = 1
            if self.camera_distance > 10:
                self.camera_distance = 10
        self.mouse_x = xpos
        self.mouse_y = ypos
        pass #print(f"{xpos}  {ypos}")

    def mouse_scroll(self, x, y):
        if y < 0.:
            self.camera_distance = self.camera_distance * 1.1
        elif y > 0:
            self.camera_distance = self.camera_distance / 1.1

        if self.camera_distance < 1:
            self.camera_distance = 1
        if self.camera_distance > 10:
            self.camera_distance = 10
        pass #print(f"{x}  {y}")

    def mouse_button(self, button, action, mods):
        if action == glfw.PRESS and button == glfw.MOUSE_BUTTON_1:
            self.rot_mode = True
        if action == glfw.RELEASE and button == glfw.MOUSE_BUTTON_1:
            self.rot_mode = False

        if action == glfw.PRESS and button == glfw.MOUSE_BUTTON_2:
            self.zoom_mode = True
        if action == glfw.RELEASE and button == glfw.MOUSE_BUTTON_2:
            self.zoom_mode = False

        pass #print(f"{button}, {action}, {mods}")

    def resize(self, w, h):
        super().resize(w, h)
        glViewport(0,0, w, h)
        self.aspect = w / h

    def update(self, T):
        self.camera_eye, self.camera_up = self.calc_eye()
        #print(f"{self.camera_eye}    {self.camera_angle_z}")
        self.Mmodel = pyrr.matrix44.create_look_at(self.camera_eye, self.camera_lookat, self.camera_up)
        self.Mproj = pyrr.matrix44.create_perspective_projection_matrix(self.camera_fovy, self.aspect, self.camera_z_near, self.camera_z_far)
        pass #print(f"{T}")

    def draw_user_interface(self):
        imgui.begin("Sample User Interface") # new window

        # draw color pickers for background and shader color
        changed, self.ui_clear_color = imgui.color_edit4("Clear Color", *self.ui_clear_color)
        changed, self.ui_shader_color = imgui.color_edit4("Tumour Color", *self.ui_shader_color)
        changed, self.ui_bias = imgui.slider_float('Fresnel Bias', self.ui_bias,-1., 1., '%.2f', 1.0)
        if changed:
            self.fresnel = [self.ui_bias, self.ui_scale, self.ui_power, self.ui_bkg_term]
        changed, self.ui_scale = imgui.slider_float('Fresnel Scale', self.ui_scale, -1., 1., '%.2f', 1.0)
        if changed:
            self.fresnel = [self.ui_bias, self.ui_scale, self.ui_power, self.ui_bkg_term]
        changed, self.ui_power = imgui.slider_float('Fresnel Power', self.ui_power, 0.0, 4.0, '%.2f', 1.0)
        if changed:
            self.fresnel = [self.ui_bias, self.ui_scale, self.ui_power, self.ui_bkg_term]

        changed, self.ui_bkg_term = imgui.slider_float('Background Visibility', self.ui_bkg_term, 0.0, 1.0, '%.2f', 1.0)
        if changed:
            self.fresnel = [self.ui_bias, self.ui_scale, self.ui_power, self.ui_bkg_term]

        #changed, self.text = imgui.input_text( "text test", self.text, 256, imgui.INPUT_TEXT_ENTER_RETURNS_TRUE)

        if (imgui.button("Save Settings")):
            self.save_settings()

        imgui.same_line()
        if (imgui.button("Quit")):
            self.keep_running = False

        imgui.end() # window ends here

    def draw(self, T):
        glClearColor(self.ui_clear_color[0],self.ui_clear_color[1],self.ui_clear_color[2],self.ui_clear_color[3])

        glUseProgram(self.shader) # This activates the shader
        glUniformMatrix4fv(self.proj_uform, 1, GL_FALSE, self.Mproj)
        glUniformMatrix4fv(self.model_uform, 1, GL_FALSE, self.Mmodel)
        glUniform4fv(self.col_uform, 1, [self.ui_shader_color]) # update the shader color
        glUniform4fv(self.bkg_uform, 1, [self.ui_clear_color]) # update the shader color
        glUniform4fv(self.fresnel_uform, 1, [self.fresnel]) # update the shader color

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # draw the triangle
        glCullFace(GL_FRONT)
        glDrawArrays(GL_TRIANGLES, 0, self.num_vertices)
        glCullFace(GL_BACK)
        glDrawArrays(GL_TRIANGLES, 0, self.num_vertices)

        if self.ui_display_menu:
            self.draw_user_interface()
