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

        self.tumour_shader = None
        self.instrument_shader = None
        self.liver_shader = None
        self.ui_clear_color = .0, .0, .3, 1.

        self.ui_tumour_color = 1.0, 1.0, 1.0, 1.0
        self.ui_tumour_bias = 0.0
        self.ui_tumour_scale = 1.0
        self.ui_tumour_power = 2.5
        self.ui_tumour_bkg_term = 0.3
        self.tumour_fresnel = [self.ui_tumour_bias, self.ui_tumour_scale, self.ui_tumour_power, self.ui_tumour_bkg_term]

        self.ui_liver_visible = True
        self.ui_liver_color = 1.0, 1.0, 1.0, 1.0
        self.ui_liver_bias = 0.0
        self.ui_liver_scale = 1.0
        self.ui_liver_power = 2.5
        self.ui_liver_bkg_term = 0.3
        self.liver_fresnel = [self.ui_liver_bias, self.ui_liver_scale, self.ui_liver_power, self.ui_liver_bkg_term]

        self.ui_instrument_visible = True
        self.ui_instrument_color = 1.0, 1.0, 1.0, 1.0
        self.ui_instrument_bias = 0.0
        self.ui_instrument_scale = 1.0
        self.ui_instrument_power = 2.5
        self.ui_instrument_bkg_term = 0.3
        self.instrument_fresnel = [self.ui_instrument_bias, self.ui_instrument_scale, self.ui_instrument_power, self.ui_instrument_bkg_term]

        self.ui_display_menu = False
        self.tumour = None
        self.tumour_center = np.array([0, 0, 0])
        self.liver = None
        self.instrument = None
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
        self.camera_lookat = np.array([0, 0, 0])
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
            if len(lines) < 28:
                raise Exception("Too few lines")
            r, g, b, a = float(lines[0]), float(lines[1]), float(lines[2]), float(lines[3])
            self.ui_clear_color = [r, g, b, a]
            r, g, b, a = float(lines[4]), float(lines[5]), float(lines[6]), float(lines[7])
            self.ui_tumour_color = [r, g, b, a]
            r, g, b, a = float(lines[8]), float(lines[9]), float(lines[10]), float(lines[11])
            self.tumour_fresnel = [r, g, b, a]
            self.ui_tumour_bias = r
            self.ui_tumour_scale = g
            self.ui_tumour_power = b
            self.ui_tumour_bkg_term = a

            r, g, b, a = float(lines[12]), float(lines[13]), float(lines[14]), float(lines[15])
            self.ui_liver_color = [r, g, b, a]
            r, g, b, a = float(lines[16]), float(lines[17]), float(lines[18]), float(lines[19])
            self.liver_fresnel = [r, g, b, a]
            self.ui_liver_bias = r
            self.ui_liver_scale = g
            self.ui_liver_power = b
            self.ui_liver_bkg_term = a

            r, g, b, a = float(lines[20]), float(lines[21]), float(lines[22]), float(lines[23])
            self.ui_instrument_color = [r, g, b, a]
            r, g, b, a = float(lines[24]), float(lines[25]), float(lines[26]), float(lines[27])
            self.instrument_fresnel = [r, g, b, a]
            self.ui_instrument_bias = r
            self.ui_instrument_scale = g
            self.ui_instrument_power = b
            self.ui_instrument_bkg_term = a
        except Exception as e:
            print(e)
            pass

    def save_settings(self):
        with open("Settings.txt", "w") as fp:
            fp.write(f"{self.ui_clear_color[0]}\n")
            fp.write(f"{self.ui_clear_color[1]}\n")
            fp.write(f"{self.ui_clear_color[2]}\n")
            fp.write(f"{self.ui_clear_color[3]}\n")

            fp.write(f"{self.ui_tumour_color[0]}\n")
            fp.write(f"{self.ui_tumour_color[1]}\n")
            fp.write(f"{self.ui_tumour_color[2]}\n")
            fp.write(f"{self.ui_tumour_color[3]}\n")

            fp.write(f"{self.tumour_fresnel[0]}\n")
            fp.write(f"{self.tumour_fresnel[1]}\n")
            fp.write(f"{self.tumour_fresnel[2]}\n")
            fp.write(f"{self.tumour_fresnel[3]}\n")

            fp.write(f"{self.ui_liver_color[0]}\n")
            fp.write(f"{self.ui_liver_color[1]}\n")
            fp.write(f"{self.ui_liver_color[2]}\n")
            fp.write(f"{self.ui_liver_color[3]}\n")

            fp.write(f"{self.liver_fresnel[0]}\n")
            fp.write(f"{self.liver_fresnel[1]}\n")
            fp.write(f"{self.liver_fresnel[2]}\n")
            fp.write(f"{self.liver_fresnel[3]}\n")

            fp.write(f"{self.ui_instrument_color[0]}\n")
            fp.write(f"{self.ui_instrument_color[1]}\n")
            fp.write(f"{self.ui_instrument_color[2]}\n")
            fp.write(f"{self.ui_instrument_color[3]}\n")

            fp.write(f"{self.instrument_fresnel[0]}\n")
            fp.write(f"{self.instrument_fresnel[1]}\n")
            fp.write(f"{self.instrument_fresnel[2]}\n")
            fp.write(f"{self.instrument_fresnel[3]}\n")
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


    def load_obj(self, model_filename):
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

        geom = conv.convert_tris(scene)
        # convert positions to 32bit float
        geom.vertex_data = np.array(geom.vertex_data, dtype = np.float32)

        geom_center = geom.calc_center()
        return geom, geom_center


    def setup(self, window, w, h):
        if not super().setup(window, w, h):
            return False

        self.aspect = w / h
        self.tumour, self.tumour_center = self.load_obj('fake_tumour.obj')
        self.liver, test4 = self.load_obj('fake_liver.obj')
        self.instrument, test2 = self.load_obj('fake_instrument.obj')

        self.tumour_shader = color_shader.create()
        self.tumour.create_geom(self.tumour_shader.pos_attrib, self.tumour_shader.uv_attrib, self.tumour_shader.nrm_attrib)

        self.liver_shader = color_shader.create()
        self.liver.create_geom(self.liver_shader.pos_attrib, self.liver_shader.uv_attrib, self.liver_shader.nrm_attrib)

        self.instrument_shader = color_shader.create()
        self.instrument.create_geom(self.instrument_shader.pos_attrib, self.instrument_shader.uv_attrib, self.instrument_shader.nrm_attrib)

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
        self.tumour.destroy()
        self.instrument.destroy()
        self.liver.destroy()

        self.tumour_shader.destroy()
        self.instrument_shader.destroy()
        self.liver_shader.destroy()
        super().finish() # call this at the last step here


    def key(self, key, scancode, action, mods):
        #print(f"key={key}  scancode={scancode}  action={action}  mods={mods}")
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            self.ui_display_menu = not self.ui_display_menu

    def mouse_enter(self, enter):
        pass #print(f"{enter}")

    def clamp_camera_values(self):
        if (self.camera_angle_side > 90):
            self.camera_angle_side = 90
        if (self.camera_angle_side < -90):
            self.camera_angle_side = -90
        if self.camera_distance < 1:
            self.camera_distance = 1
        if self.camera_distance > 15:
            self.camera_distance = 15

    def mouse_move(self, xpos, ypos):
        scale_dx = 1.
        scale_dy = 1.
        if self.rot_mode:
            dx = xpos - self.mouse_x
            dy = ypos - self.mouse_y
            self.camera_angle_up = self.camera_angle_up + dx * scale_dx
            self.camera_angle_side = self.camera_angle_side + dy * scale_dy
            self.clamp_camera_values()
        if self.zoom_mode:
            dy = ypos - self.mouse_y
            self.camera_distance = self.camera_distance + dy * 0.01
            self.clamp_camera_values()
        self.mouse_x = xpos
        self.mouse_y = ypos

    def mouse_scroll(self, x, y):
        if y < 0.:
            self.camera_distance = self.camera_distance * 1.1
        elif y > 0:
            self.camera_distance = self.camera_distance / 1.1
        self.clamp_camera_values()

    def mouse_button(self, button, action, mods):
        if action == glfw.PRESS and button == glfw.MOUSE_BUTTON_1:
            self.rot_mode = True
        if action == glfw.RELEASE and button == glfw.MOUSE_BUTTON_1:
            self.rot_mode = False

        if action == glfw.PRESS and button == glfw.MOUSE_BUTTON_2:
            self.zoom_mode = True
        if action == glfw.RELEASE and button == glfw.MOUSE_BUTTON_2:
            self.zoom_mode = False

    def resize(self, w, h):
        super().resize(w, h)
        glViewport(0,0, w, h)
        self.aspect = w / h

    def update(self, T):
        self.camera_eye, self.camera_up = self.calc_eye()
        self.camera_eye += self.tumour_center
        self.camera_lookat = self.tumour_center
        #print(f"{self.camera_eye}    {self.camera_angle_z}")
        self.Mmodel = pyrr.matrix44.create_look_at(self.camera_eye, self.camera_lookat, self.camera_up)
        self.Mproj = pyrr.matrix44.create_perspective_projection_matrix(self.camera_fovy, self.aspect, self.camera_z_near, self.camera_z_far)
        pass #print(f"{T}")

    def draw_user_interface(self):
        imgui.begin("Sample User Interface") # new window

        # draw color pickers for background and shader color
        imgui.text("Clear   : ")
        imgui.same_line()
        changed, self.ui_clear_color = imgui.color_edit4("##Clear_Color", *self.ui_clear_color)

        opened, _ = imgui.collapsing_header("Tumour")
        if opened:
            imgui.text("Color   : ")
            imgui.same_line()
            changed, self.ui_tumour_color = imgui.color_edit4("##Tumour_Color", *self.ui_tumour_color)
            imgui.text("Bias    : ")
            imgui.same_line()
            changed, self.ui_tumour_bias = imgui.slider_float('##Tumour_Bias', self.ui_tumour_bias,-1., 1., '%.2f', 1.0)
            if changed:
                self.tumour_fresnel = [self.ui_tumour_bias, self.ui_tumour_scale, self.ui_tumour_power, self.ui_tumour_bkg_term]
            imgui.text("Scale   : ")
            imgui.same_line()
            changed, self.ui_tumour_scale = imgui.slider_float('##Tumour_Scale', self.ui_tumour_scale, -1., 1., '%.2f', 1.0)
            if changed:
                self.tumour_fresnel = [self.ui_tumour_bias, self.ui_tumour_scale, self.ui_tumour_power, self.ui_tumour_bkg_term]
            imgui.text("Power   : ")
            imgui.same_line()
            changed, self.ui_tumour_power = imgui.slider_float('##Tumour_Power', self.ui_tumour_power, 0.0, 4.0, '%.2f', 1.0)
            if changed:
                self.tumour_fresnel = [self.ui_tumour_bias, self.ui_tumour_scale, self.ui_tumour_power, self.ui_tumour_bkg_term]
            imgui.text("Backside: ")
            imgui.same_line()
            changed, self.ui_tumour_bkg_term = imgui.slider_float('##Tumour_Backside', self.ui_tumour_bkg_term, 0.0, 1.0, '%.2f', 1.0)
            if changed:
                self.tumour_fresnel = [self.ui_tumour_bias, self.ui_tumour_scale, self.ui_tumour_power, self.ui_tumour_bkg_term]
        opened, _ = imgui.collapsing_header("Liver")
        if opened:
            imgui.text("Visible : ")
            imgui.same_line()
            changed, state = imgui.checkbox("##Liver_Visible", self.ui_liver_visible)
            if changed:
                self.ui_liver_visible = state
            imgui.text("Color   : ")
            imgui.same_line()
            changed, self.ui_liver_color = imgui.color_edit4("##Liver_Color", *self.ui_liver_color)
            imgui.text("Bias    : ")
            imgui.same_line()
            changed, self.ui_liver_bias = imgui.slider_float('##Liver_Bias', self.ui_liver_bias,-1., 1., '%.2f', 1.0)
            if changed:
                self.liver_fresnel = [self.ui_liver_bias, self.ui_liver_scale, self.ui_liver_power, self.ui_liver_bkg_term]
            imgui.text("Scale   : ")
            imgui.same_line()
            changed, self.ui_liver_scale = imgui.slider_float('##Liver_Scale', self.ui_liver_scale, -1., 1., '%.2f', 1.0)
            if changed:
                self.liver_fresnel = [self.ui_liver_bias, self.ui_liver_scale, self.ui_liver_power, self.ui_liver_bkg_term]
            imgui.text("Power   : ")
            imgui.same_line()
            changed, self.ui_liver_power = imgui.slider_float('##Liver_Power', self.ui_liver_power, 0.0, 4.0, '%.2f', 1.0)
            if changed:
                self.liver_fresnel = [self.ui_liver_bias, self.ui_liver_scale, self.ui_liver_power, self.ui_liver_bkg_term]
            imgui.text("Backside: ")
            imgui.same_line()
            changed, self.ui_liver_bkg_term = imgui.slider_float('##Liver_Backside', self.ui_liver_bkg_term, 0.0, 1.0, '%.2f', 1.0)
            if changed:
                self.liver_fresnel = [self.ui_liver_bias, self.ui_liver_scale, self.ui_liver_power, self.ui_liver_bkg_term]

        opened, _ = imgui.collapsing_header("Instrument")
        if opened:
            imgui.text("Visible : ")
            imgui.same_line()
            changed, state = imgui.checkbox("##Instrument_Visible", self.ui_instrument_visible)
            if changed:
                self.ui_instrument_visible = state
            imgui.text("Color   : ")
            imgui.same_line()
            changed, self.ui_instrument_color = imgui.color_edit4("##Instrument_Color", *self.ui_instrument_color)
            imgui.text("Bias    : ")
            imgui.same_line()
            changed, self.ui_instrument_bias = imgui.slider_float('##Instrument_Bias', self.ui_instrument_bias,-1., 1., '%.2f', 1.0)
            if changed:
                self.instrument_fresnel = [self.ui_instrument_bias, self.ui_instrument_scale, self.ui_instrument_power, self.ui_instrument_bkg_term]
            imgui.text("Scale   : ")
            imgui.same_line()
            changed, self.ui_instrument_scale = imgui.slider_float('##Instrument_Scale', self.ui_instrument_scale, -1., 1., '%.2f', 1.0)
            if changed:
                self.instrument_fresnel = [self.ui_instrument_bias, self.ui_instrument_scale, self.ui_instrument_power, self.ui_instrument_bkg_term]
            imgui.text("Power   : ")
            imgui.same_line()
            changed, self.ui_instrument_power = imgui.slider_float('##Instrument_Power', self.ui_instrument_power, 0.0, 4.0, '%.2f', 1.0)
            if changed:
                self.instrument_fresnel = [self.ui_instrument_bias, self.ui_instrument_scale, self.ui_instrument_power, self.ui_instrument_bkg_term]
            imgui.text("Backside: ")
            imgui.same_line()
            changed, self.ui_instrument_bkg_term = imgui.slider_float('##Instrument_Backside', self.ui_instrument_bkg_term, 0.0, 1.0, '%.2f', 1.0)
            if changed:
                self.instrument_fresnel = [self.ui_instrument_bias, self.ui_instrument_scale, self.ui_instrument_power, self.ui_instrument_bkg_term]


        #changed, self.text = imgui.input_text( "text test", self.text, 256, imgui.INPUT_TEXT_ENTER_RETURNS_TRUE)

        if (imgui.button("Save Settings")):
            self.save_settings()

        imgui.same_line()
        if (imgui.button("Quit")):
            self.keep_running = False

        imgui.end() # window ends here

    def draw(self, T):
        glClearColor(self.ui_clear_color[0],self.ui_clear_color[1],self.ui_clear_color[2],self.ui_clear_color[3])

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # draw the tumour
        self.tumour_shader.run(self.Mproj, self.Mmodel, self.ui_tumour_color, self.ui_clear_color, self.tumour_fresnel)
        self.tumour.use()
        glCullFace(GL_FRONT)
        glDrawArrays(GL_TRIANGLES, 0, self.tumour.count_verts())
        glCullFace(GL_BACK)
        glDrawArrays(GL_TRIANGLES, 0, self.tumour.count_verts())

        if self.ui_liver_visible:
            self.liver_shader.run(self.Mproj, self.Mmodel, self.ui_liver_color, self.ui_clear_color, self.liver_fresnel)
            self.liver.use()
            glCullFace(GL_FRONT)
            glDrawArrays(GL_TRIANGLES, 0, self.liver.count_verts())
            glCullFace(GL_BACK)
            glDrawArrays(GL_TRIANGLES, 0, self.liver.count_verts())

        if self.ui_instrument_visible:
            self.instrument_shader.run(self.Mproj, self.Mmodel, self.ui_instrument_color, self.ui_clear_color, self.instrument_fresnel)
            self.instrument.use()
            glCullFace(GL_FRONT)
            glDrawArrays(GL_TRIANGLES, 0, self.instrument.count_verts())
            glCullFace(GL_BACK)
            glDrawArrays(GL_TRIANGLES, 0, self.instrument.count_verts())

        if self.ui_display_menu:
            self.draw_user_interface()
