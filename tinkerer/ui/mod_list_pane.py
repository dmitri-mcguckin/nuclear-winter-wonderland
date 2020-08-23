import curses
import tinkerer.modpack as modpack


class ModListPane:
    def __init__(self, parent, pack: modpack.ModPack):
        self.parent = parent
        self.window = curses.newpad(1, 1)
        self.window.scrollok(True)
        self.pack = pack
        self.selected = False
        self.scroll_position = 0
        self.resize()

    def read_input(self, key):
        # Read the key input
        if(key == curses.KEY_UP):
            self.scroll_position -= 1
        elif(key == curses.KEY_DOWN):
            self.scroll_position += 1

        # Do Scroll bounds checking
        if(self.scroll_position < 0):
            self.scroll_position = 0
        elif(self.scroll_position > len(self.pack.mods) - 1):
            self.scroll_position = len(self.pack.mods) - 1

    def resize(self):
        py_off, px_off = self.parent.getyx()
        pheight, pwidth = self.parent.getmaxyx()
        pwidth -= 2
        pheight -= 2

        self.height = pheight
        self.width = pwidth
        self.x_offset = int(pwidth / 3)
        self.y_offset = py_off + 1

        pad_width = self.width

        if(len(self.pack.mods) < self.height):
            pad_height = self.height
        else:
            pad_height = len(self.pack.mods) + 1

        self.window.resize(pad_height, pad_width)
        self.window.clear()

    def draw(self):
        self.window.box()

        if(self.selected):
            self.window.attron(curses.A_REVERSE)
        self.window.addstr(0, 1, 'Mods ({})'.format(len(self.pack.mods)))
        self.window.attroff(curses.A_REVERSE)

        for i, m in enumerate(self.pack.mods):
            if(self.selected and i == self.scroll_position):
                self.window.attron(curses.A_REVERSE)
            self.window.addstr(i + 1,  1, m.name)
            self.window.attroff(curses.A_REVERSE)

        scroll_offset = self.scroll_position
        if(self.scroll_position + (self.height - 1) > len(self.pack.mods)):
            scroll_offset = len(self.pack.mods) - (self.height - 1)

        self.window.refresh(scroll_offset,
                            0,
                            self.y_offset,
                            self.x_offset,
                            self.height,
                            self.width)

    def hovered_mod(self):
        if(len(self.pack.mods) > 0):
            return self.pack.mods[self.scroll_position]
        else:
            return None
