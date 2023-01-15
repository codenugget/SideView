from OpenGL.GL import *
import glfw
import imgui
from imgui.integrations.glfw import GlfwRenderer

import ConvertModel as mod

def main():
    if not glfw.init():
        print("ERROR: Unable to intiailize glfw")
        return

    cur_module = mod.ConvertModel()

    glfw.window_hint(glfw.DEPTH_BITS, 1)
    glfw.window_hint(glfw.STENCIL_BITS, 0)
    glfw.window_hint(glfw.DOUBLEBUFFER, True)

    # Need to be declared global since the values are written to in local function resize below
    global width, height
    width = 720
    height = 600
    if cur_module.desired_width > 0:
        width = cur_module.desired_width
    if cur_module.desired_height > 0:
        height = cur_module.desired_height

    window = glfw.create_window(width, height, cur_module.title, None, None) 
    if not window:
        print("ERROR: Unable to create an OpenGL window")
        glfw.terminate()
        return
    glfw.make_context_current(window)

    if not cur_module.setup(window, width, height):
        print("ERROR: Unable to setup the module")
        glfw.terminate()
        return

    # initilize imgui context
    imgui.create_context()
    io = imgui.get_io()
    io.display_size = width, height
    io.fonts.get_tex_data_as_rgba32()

    def resize(win, w, h):
        global width, height
        width = w
        height = h
        cur_module.resize(width, height)

    def mouse_enter(win, entered):
        cur_module.mouse_enter(entered)
    def mouse_move(win, x, y):
        if not io.want_capture_mouse:
            cur_module.mouse_move(x, y)
    def mouse_scroll(win, x, y):
        if not io.want_capture_mouse:
            cur_module.mouse_scroll(x, y)
    def mouse_button(win, button, action, mods):
        if not io.want_capture_mouse:
            cur_module.mouse_button(button, action, mods)
    def key(win, key, scancode, action, mods):
        if not io.want_capture_keyboard:
            cur_module.key(key, scancode, action, mods)

    # NOTE:
    #   GlfwRenderer(window) must be above the X_callback(...) methods below.
    #   Otherwise it will override the callbacks and no events are sent to the module.
    impl = GlfwRenderer(window)

    glfw.set_framebuffer_size_callback(window, resize)
    glfw.set_cursor_enter_callback(window, mouse_enter)
    glfw.set_cursor_pos_callback(window, mouse_move)
    glfw.set_scroll_callback(window, mouse_scroll)
    glfw.set_mouse_button_callback(window, mouse_button)
    glfw.set_key_callback(window, key)

    glfw.set_time(0.0)
    while cur_module.keep_running and not glfw.window_should_close(window):
        # start new frame context
        impl.process_inputs()
        imgui.new_frame()

        glfw.poll_events()

        Time = glfw.get_time()
        cur_module.update(Time)
        cur_module.draw(Time)

        # pass all drawing comands to the rendering pipeline
        # and close frame context
        imgui.render()
        impl.render(imgui.get_draw_data())
        imgui.end_frame()

        glfw.swap_buffers(window)

    cur_module.finish()
    glfw.terminate()

if __name__ == "__main__":
    main()
