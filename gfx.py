class Base:
    def __init__(self):
        self.title = ""
        self.width = 0
        self.height = 0
        self.desired_width = 0
        self.desired_height = 0
        self.keep_running = True
        self.window = None

    def setup(self, window, w, h):
        self.window = window
        self.width = w
        self.height = h
        return True

    def finish(self):
        pass

    def resize(self, w, h):
        self.width = w
        self.height = h

    def update(self, T):
        pass

    def draw(self, T):
        pass

    def mouse_enter(self, enter):
        pass

    def mouse_move(self, xpos, ypos):
        pass

    def mouse_scroll(self, x, y):
        pass

    def mouse_button(self, button, action, mods):
        pass

    def key(self, key, scancode, action, mods):
        pass