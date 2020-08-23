import curses
import tinkerer.mod as mod
import tinkerer.modpack as modpack
from tinkerer.ui.sub_windows import SelectionWindow, \
                                    InputWindow, \
                                    PopupWindow


class ModInfoPane:
    def __init__(self, parent, pack: modpack.ModPack):
        # Curses window things
        self.parent = parent
        self.window = curses.newpad(1, 1)

        # UI + Input things
        self.pack = pack
        self.selected = False
        self.scroll_pos = 0

        self.entries = [
            'error: no mod name available',
            'error: no project id available',
            'error: no file id available',
            'error: no required flag available',
            '\t[ Remove Mod ]'
        ]

        # Reform the UI
        self.resize()

    def resize(self):
        py_off, px_off = self.parent.getyx()
        pheight, pwidth = self.parent.getmaxyx()
        pwidth -= 2
        pheight -= 2

        self.height = int(pheight / 2) + 2
        self.width = int(pwidth / 3) - 1
        self.x_offset = 1
        self.y_offset = py_off + + int(pheight / 2)

        self.window.resize(self.height, self.width)
        self.window.clear()

    def draw(self, mod: mod.Mod):
        self.window.clear()
        self.window.box()

        if(mod is not None):
            self.entries[0] = mod.name
            self.entries[1] = '\tProject ID:'.ljust(15, ' ') + str(mod.project_id)
            self.entries[2] = '\tFile ID:'.ljust(15, ' ') + str(mod.file_id)
            self.entries[3] = '\tRequired:'.ljust(15, ' ') + str(mod.required)

        if(self.selected):
            self.window.attron(curses.A_REVERSE)
        self.window.addstr(0, 1, 'Mod-Details:')
        self.window.attroff(curses.A_REVERSE)

        if(mod is not None):
            for i, e in enumerate(self.entries):
                if(self.selected and i == self.scroll_pos):
                    self.window.attron(curses.A_REVERSE)
                if(i == len(self.entries) - 1):
                    self.window.attron(curses.color_pair(3))
                self.window.addstr(2 + i, 2, e)
                self.window.attroff(curses.A_REVERSE)
                self.window.attroff(curses.color_pair(3))

        self.window.refresh(0,
                            0,
                            self.y_offset,
                            self.x_offset,
                            self.height + self.y_offset,
                            self.width + self.x_offset)

    def read_input(self, key, hovered_mod: mod.Mod) -> int:
        action = 0

        # Check user input
        if(key == curses.KEY_UP):
            self.scroll_pos -= 1
        elif(key == curses.KEY_DOWN):
            self.scroll_pos += 1
        elif(key == 10):
            if(hovered_mod is None):
                PopupWindow(self.parent, 'No mod to edit!')
            else:
                action = self.modify_mod(hovered_mod)

        # Bounds checking
        if(self.scroll_pos < 0):
            self.scroll_pos = 0
        elif(self.scroll_pos >= len(self.entries)):
            self.scroll_pos = len(self.entries) - 1
        return action

    def modify_mod(self, hovered_mod: mod.Mod) -> int:
        action = 0

        if(self.scroll_pos == 0):
            success = self.edit_name(hovered_mod)
        elif(self.scroll_pos == 1):
            success = self.edit_project_id(hovered_mod)
        elif(self.scroll_pos == 2):
            success = self.edit_file_id(hovered_mod)
        elif(self.scroll_pos == 3):
            success = self.edit_required(hovered_mod)
        elif(self.scroll_pos == (len(self.entries) - 1)):
            self.pack.remove(hovered_mod)
            success = True
            action = 2

        if(success and action != 2):
            action = 1

        self.resize()
        return action

    def edit_name(self, hovered_mod: mod.Mod) -> bool:
        success = False
        input = InputWindow(self.parent,
                            banner='Edit Mod: Name',
                            color_pair=2)
        new_name = input.start()
        if(new_name != ''):
            hovered_mod.name = new_name
            success = True
        else:
            PopupWindow(self.parent, 'Name cannot be empty!')
        return success

    def edit_project_id(self, hovered_mod: mod.Mod) -> bool:
        success = False
        input = InputWindow(self.parent,
                            banner='Edit Mod: Project ID',
                            color_pair=2)
        try:
            new_project_id = int(input.start(InputWindow.is_numeric))
            hovered_mod.project_id = new_project_id
            success = True
        except Exception:
            PopupWindow(self.parent, 'Project id cannot be empty!')
        return success

    def edit_file_id(self, hovered_mod: mod.Mod) -> bool:
        success = False
        input = InputWindow(self.parent,
                            banner='Edit Mod: File ID',
                            color_pair=2)
        try:
            new_file_id = int(input.start(InputWindow.is_numeric))
            hovered_mod.file_id = new_file_id
            success = True
        except Exception:
            PopupWindow(self.parent, 'File id cannot be empty!')
        return success

    def edit_required(self, hovered_mod: mod.Mod) -> bool:
        prev_state = hovered_mod.required
        input = SelectionWindow(self.parent,
                                [True, False],
                                banner='Required?')
        required = input.start()
        hovered_mod.required = required
        return hovered_mod.required != prev_state
