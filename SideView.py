from OpenGL.GL import *

import glfw
import imgui
import numpy as np

import color_shader
import gfx

class SideView(gfx.Base):
    def __init__(self):
        super().__init__()
        self.title = "Side View"
        self.desired_width = 1024
        self.desired_height = 768

        self.shader = -1
        self.pos_attr = -1
        self.col_attr = -1
        self.col_uform = -1
        self.clear_color = .0, .0, .3, 1.
        self.shader_color = 1.0, 1.0, 1.0, 1.0
        self.num_vertices = 0
        self.vertex_data = []
        self.text = str()


    def setup(self, window, w, h):
        if not super().setup(window, w, h):
            return False

        self.shader, self.pos_attr, self.col_attr, self.col_uform = color_shader.create()

        self.num_vertices = 3
        num_vertex_elements = 3 + 4 # 3 for position.xyz, 4 for color.rgba
        element_size = 4 # size of float
        vertex_attrib_bytes = num_vertex_elements * element_size
        num_array_bytes = self.num_vertices * vertex_attrib_bytes
        skip_vertex_bytes = 3 * 4
        #skip_color_bytes = skip_vertex_bytes + 4 * 4
        # xyz, rgba
        self.vertex_data = [
            -0.5,-0.5, 0.0, 1.0, 0.0, 0.0, 1.0,
            0.5,-0.5, 0.0, 0.0, 1.0, 0.0, 1.0,
            0.0, 0.5, 0.0, 0.0, 0.0, 1.0, 1.0,
        ]
        # convert positions to 32bit float
        self.vertex_data = np.array(self.vertex_data, dtype = np.float32)

        # Create buffer object
        self.vertex_buffer_object = glGenBuffers(1) 

        # Bind the buffer and setup the attrib arrays
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer_object)
        glBufferData(GL_ARRAY_BUFFER, num_array_bytes, self.vertex_data, GL_STATIC_DRAW)

        glVertexAttribPointer(self.pos_attr, 3, GL_FLOAT, GL_FALSE, vertex_attrib_bytes, None)
        glEnableVertexAttribArray(self.pos_attr)
        glVertexAttribPointer(self.col_attr, 4, GL_FLOAT, GL_FALSE, vertex_attrib_bytes, ctypes.c_void_p(skip_vertex_bytes))
        glEnableVertexAttribArray(self.col_attr)

        glUseProgram(self.shader) # This activates the shader
        #glUseProgram(0) # This can be used to disable the shader (when desired)

        # enable rendering to be transparent
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        return True


    def finish(self):
        # cleanup here
        glDeleteBuffers(1, [self.vertex_buffer_object])
        super().finish() # call this at the last step here


    def key(self, key, scancode, action, mods):
        #print(f"key={key}  scancode={scancode}  action={action}  mods={mods}")
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            self.keep_running = False

    def mouse_enter(self, enter):
        pass #print(f"{enter}")

    def mouse_move(self, xpos, ypos):
        pass #print(f"{xpos}  {ypos}")

    def mouse_scroll(self, x, y):
        pass #print(f"{x}  {y}")

    def mouse_button(self, button, action, mods):
        pass #print(f"{button}, {action}, {mods}")

    def resize(self, w, h):
        glViewport(0,0, w, h)

    def update(self, T):
        pass #print(f"{T}")

    def draw_user_interface(self):
        imgui.begin("Sample User Interface") # new window

        # draw color pickers for background and shader color
        changed, self.clear_color = imgui.color_edit4("Clear Color", *self.clear_color)
        changed, self.shader_color = imgui.color_edit4("Shader Color", *self.shader_color)
        #changed, self.text = imgui.input_text( "text test", self.text, 256, imgui.INPUT_TEXT_ENTER_RETURNS_TRUE)

        if (imgui.button("Quit")):
            self.keep_running = False
        imgui.end() # window ends here

    def draw(self, T):
        glClearColor(self.clear_color[0],self.clear_color[1],self.clear_color[2],self.clear_color[3])

        glUseProgram(self.shader) # This activates the shader
        glUniform4fv(self.col_uform, 1, [self.shader_color]) # update the shader color

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # draw the triangle
        glDrawArrays(GL_TRIANGLES, 0, self.num_vertices)

        self.draw_user_interface()
