import curses
import tinkerer.mod as mod
import tinkerer.modpack as modpack
from tinkerer.ui.sub_windows import InputWindow, \
                                    SelectionWindow, \
                                    PopupWindow


class ModListPane:
    def __init__(self, parent, pack: modpack.ModPack):
        self.parent = parent
        self.window = curses.newpad(1, 1)
        self.window.scrollok(True)
        self.pack = pack
        self.selected = False
        self.scroll_position = 0
        self.resize()

    def read_input(self, key) -> int:
        action = 0
        self.window.clear()

        # Read the key input
        if(key == curses.KEY_UP and self.scroll_position > 0):
            self.scroll_position -= 1
        elif(key == curses.KEY_DOWN
             and self.scroll_position <= len(self.pack.mods) - 1):
            self.scroll_position += 1
        elif(key == 567 or key == 546):  # Ctrl+Up or Ctrl+Left
            self.scroll_position -= 10

            if(self.scroll_position < 1):
                self.scroll_position = 1
        elif(key == 526 or key == 561):  # Ctrl+Down or Ctrl+Right
            self.scroll_position += 10

            if(self.scroll_position >= len(self.pack.mods)):
                self.scroll_position = len(self.pack.mods)
        elif(key == 10 and self.scroll_position == 0):
            try:
                new_mod = self.create_new_mod()
                self.pack.add(new_mod)
                action = 1
            except ValueError as e:
                PopupWindow(self.parent, str(e))
        return action

    def resize(self):
        py_off, px_off = self.parent.getyx()
        pheight, pwidth = self.parent.getmaxyx()

        self.height = pheight - 2
        self.width = pwidth - 3
        self.x_offset = int(pwidth / 3)
        self.y_offset = py_off + 1

        self.window.resize(self.height, self.width)
        self.window.clear()

    def draw(self):
        if(self.selected):
            self.window.attron(curses.A_REVERSE)
        self.window.addstr(0, 0, 'Mods ({})'.format(len(self.pack.mods)))
        self.window.attroff(curses.A_REVERSE)

        if(self.selected and self.scroll_position == 0):
            self.window.attron(curses.A_REVERSE | curses.color_pair(1))
        self.window.addstr(0, 15, '[ Add Mod ]')
        self.window.attroff(curses.A_REVERSE | curses.color_pair(1))

        sub_pane = curses.newpad(len(self.pack.mods) + 5, self.width)

        for i, m in enumerate(self.pack.sorted_mods()):
            i += 1
            if(i == self.scroll_position):
                sub_pane.attron(curses.A_REVERSE)
            sub_pane.addstr(i - 1,  1, m.name)
            sub_pane.attroff(curses.A_REVERSE)

        scroll_offset = self.scroll_position
        if(self.scroll_position + (self.height - 2) > len(self.pack.mods)):
            scroll_offset = len(self.pack.mods) - (self.height - 2)

        self.window.refresh(0,
                            0,
                            self.y_offset,
                            self.x_offset,
                            self.height,
                            self.width)
        sub_pane.refresh(scroll_offset - 1,
                         0,
                         self.y_offset + 1,
                         self.x_offset + 1,
                         self.height,
                         self.width)

    def hovered_mod(self):
        if(len(self.pack.mods) > 0):
            if(self.scroll_position == 0):
                return None
            else:
                return self.pack[self.scroll_position - 1]
        else:
            return None

    def create_new_mod(self) -> mod.Mod:
        input_window = InputWindow(self.parent,
                                   banner='New Mod: Name',
                                   color_pair=2)
        name = input_window.start()
        if(name == ''):
            raise ValueError('Name cannot be empty!')

        input_window = InputWindow(self.parent,
                                   banner='New Mod: Project ID',
                                   color_pair=2)
        try:
            project_id = int(input_window.start(validator=InputWindow.is_numeric))
        except Exception:
            raise ValueError('Project ID cannot be empty and must be alphanumeric!')

        input_window = InputWindow(self.parent,
                                   banner='New Mod: File ID',
                                   color_pair=2)
        try:
            file_id = int(input_window.start(validator=InputWindow.is_numeric))
        except Exception:
            raise ValueError('File ID cannot be empty and must be alphanumeric!')

        input_window = SelectionWindow(self.parent,
                                       [True, False],
                                       banner='New Mod: Required?:',
                                       color_pair=2)
        required = input_window.start()
        return mod.Mod(name, project_id, file_id, required)
