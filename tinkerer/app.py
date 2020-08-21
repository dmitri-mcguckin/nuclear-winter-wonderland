import os
import re
import json
import time
import curses
import tinkerer
import tinkerer.mod as mod
import tinkerer.modpack as modpack
import tinkerer.registry as registry
from curses.textpad import Textbox


class PopupWindow:
    def __init__(self, parent, message, banner='fatal', color_pair=3):
        height, width = parent.getmaxyx()
        style = curses.color_pair(color_pair) | curses.A_REVERSE
        any_key_message = "Press any key to continue..."
        message = message.split('\n')
        long = len(any_key_message)

        for m in message:
            if(len(m) > long):
                long = len(m)
        if(long < len(banner)):
            long = len(banner)

        window = curses.newwin(len(message) + 2,
                               long + 2,
                               int((height - len(message) + 2) / 2),
                               int((width - long + 2) / 2))
        window.attron(style)
        for i, m in enumerate(message):
            window.addstr(1 + i, 1, m.ljust(long, ' '))
        window.box()
        window.addstr(0, 1, banner + ":", curses.A_UNDERLINE | style)
        window.addstr(len(message) + 1,
                      long - len(any_key_message),
                      any_key_message)

        window.attroff(style)

        window.refresh()
        parent.refresh()

        window.getch()
        curses.flushinp()
        window.clear()
        parent.clear()


class SelectionWindow:
    def __init__(self, parent, options, banner='Select One', color_pair=3):
        height, width = parent.getmaxyx()

        long = len(banner)

        for m in options:
            if(len(m) > long):
                long = len(m)
        if(long < len(banner)):
            long = len(banner)

        self.banner = banner
        self.options = options
        self.selection = 0
        self.confirmed = None
        self.parent = parent
        self.window = curses.newwin(len(options) + 2,
                                    long + 2,
                                    int((height - len(options) + 2) / 2),
                                    int((width - long + 2) / 2))
        self.window.keypad(True)        # Enable special key input
        self.window.nodelay(True)       # Disable user-input blocking
        curses.cbreak(True)
        curses.noecho()        # Disables echo

    def start(self):
        while self.confirmed is None:
            self.read_input()

            self.window.box()
            self.window.addstr(0, 1, self.banner)

            for i, option in enumerate(self.options):
                option = option.split('.')[0].replace('-', ' ').title()
                if(i == self.selection):
                    self.window.attron(curses.A_REVERSE)
                self.window.addstr(i + 1, 1, '{}.) {}'.format(i + 1, option))
                self.window.attroff(curses.A_REVERSE)

            self.window.refresh()
        return self.confirmed

    def read_input(self):
        # Grab new user input and immediately flush the buffer
        key = self.window.getch()
        curses.flushinp()

        # Determine the key input
        if(key == curses.KEY_UP):
            self.selection -= 1
        elif(key == curses.KEY_DOWN):
            self.selection += 1
        elif(key == 10):
            self.confirmed = self.options[self.selection]

        if(self.selection < 0):
            self.selection = 0
        elif(self.selection >= len(self.options)):
            self.selection = len(self.options) - 1


class InputWindow:
    def __init__(self, parent, banner='Input', color_pair=3):
        height, width = parent.getmaxyx()

        long = 64

        self.banner = banner
        self.parent = parent
        self.x_off = int((width - long + 2) / 2)
        self.y_off = int((height - 5) / 2)
        self.window = curses.newwin(5, long + 2, self.y_off, self.x_off)
        self.window.keypad(True)        # Enable special key input
        self.window.nodelay(True)       # Disable user-input blocking
        self.color_pair = color_pair
        curses.raw()            # Enable raw input (DISABLES SIGNALS)
        curses.noecho()         # Disable user-input echo
        curses.cbreak()         # Disable line-buffering (less input delay)
        curses.curs_set(True)  # Enable the cursor display

    def start(self, validator=None):
        width = 32
        height = 1
        x_off = self.x_off + 2
        y_off = self.y_off + 2
        input = curses.newwin(height,
                              width,
                              y_off,
                              x_off)
        box = Textbox(input)
        box.stripspaces = True

        self.window.attron(curses.color_pair(self.color_pair))
        self.window.box()
        self.window.addstr(0, 1, self.banner)
        self.window.refresh()

        box.edit(validator)
        self.window.attroff(curses.color_pair(self.color_pair))
        curses.curs_set(False)  # Disable the cursor display
        return box.gather().strip()

    def is_numeric(key):
        search = re.match('[0-9]', chr(key))

        if(search is not None):
            return search.string
        elif(key == 10):
            return key
        else:
            return None


class ModPackInfoPane:
    def __init__(self, parent):
        self.parent = parent
        self.window = curses.newpad(1, 1)
        self.selected = True
        self.scroll_pos = 0
        self.resize()

    def resize(self):
        py_off, px_off = self.parent.getyx()
        pheight, pwidth = self.parent.getmaxyx()
        pwidth -= 2
        pheight -= 2

        self.height = int(pheight / 2) - 1
        self.width = int(pwidth / 3) - 1
        self.x_offset = px_off + 1
        self.y_offset = py_off + 1

        self.window.resize(self.height, self.width)
        self.window.clear()

    def draw(self, pack: modpack.ModPack):
        self.window.box()

        if(self.selected):
            self.window.attron(curses.A_REVERSE)
        self.window.addstr(0, 1, 'Pack Details:')
        self.window.attroff(curses.A_REVERSE)

        entries = [
            pack.name,
            '\tBy: {}'.format(pack.author),
            '\tPack Version: v{}'.format(pack.pack_version),
            '\tMC Version: v{}'.format(pack.mc_version),
            '\tSponge Version: v{}'.format(pack.sponge_version)
        ]

        for i, e in enumerate(entries):
            if(self.selected and i == self.scroll_pos):
                self.window.attron(curses.A_REVERSE)
            self.window.addstr(2 + i, 2, e)
            self.window.attroff(curses.A_REVERSE)

        self.window.refresh(0,
                            0,
                            self.y_offset,
                            self.x_offset,
                            self.height + self.y_offset,
                            self.width + self.x_offset)

    def read_input(self, key):
        if(key == curses.KEY_UP):
            self.scroll_pos -= 1
        elif(key == curses.KEY_DOWN):
            self.scroll_pos += 1
        elif(key == 10):
            input = InputWindow(self.window, banner='Edit Pack: Name', color_pair=2)
            new_name = input.start()

        if(self.scroll_pos < 0):
            self.scroll_pos = 0
        elif(self.scroll_pos > 4):
            self.scroll_pos = 4


class ModInfoPane:
    def __init__(self, parent):
        self.parent = parent
        self.window = curses.newpad(1, 1)
        self.resize()

    def resize(self):
        py_off, px_off = self.parent.getyx()
        pheight, pwidth = self.parent.getmaxyx()
        pwidth -= 2
        pheight -= 2

        self.height = int(pheight / 2) + 2
        self.width = int(pwidth / 3) - 1
        self.x_offset = px_off + 1
        self.y_offset = py_off + + int(pheight / 2)

        self.window.resize(self.height, self.width)
        self.window.clear()

    def draw(self, mod: mod.Mod):
        self.window.clear()
        self.window.box()
        self.window.addstr(0, 1, "Mod Details:")

        if(mod is not None):
            self.window.addstr(2, 2, mod.name)
            self.window.addstr(3, 2, '\tProject ID:'
                                     .ljust(13, ' ')
                                     + str(mod.project_id))
            self.window.addstr(4, 2, '\tFile ID:'
                                     .ljust(13, ' ')
                                     + str(mod.file_id))

            if(mod.required):
                self.window.attron(curses.A_REVERSE)
                self.window.addstr(6,
                                   2,
                                   '[REQUIRED MOD]',
                                   curses.color_pair(3))
            self.window.attroff(curses.A_REVERSE)

        self.window.refresh(0,
                            0,
                            self.y_offset,
                            self.x_offset,
                            self.height + self.y_offset,
                            self.width + self.x_offset)


class ModsPane:
    def __init__(self, parent, mods):
        self.parent = parent
        self.window = curses.newpad(1, 1)
        self.window.scrollok(True)
        self.mods = mods
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
        elif(self.scroll_position > len(self.mods) - 1):
            self.scroll_position = len(self.mods) - 1

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

        if(len(self.mods) < self.height):
            pad_height = self.height
        else:
            pad_height = len(self.mods) + 1

        self.window.resize(pad_height, pad_width)
        self.window.clear()

    def draw(self):
        self.window.box()

        if(self.selected):
            self.window.attron(curses.A_REVERSE)
        self.window.addstr(0, 1, 'Mods ({})'.format(len(self.mods)))
        self.window.attroff(curses.A_REVERSE)

        for i, m in enumerate(self.mods):
            if(self.selected and i == self.scroll_position):
                self.window.attron(curses.A_REVERSE)
            self.window.addstr(i + 1,  1, m.name)
            self.window.attroff(curses.A_REVERSE)

        scroll_offset = self.scroll_position
        if(self.scroll_position + (self.height - 1) > len(self.mods)):
            scroll_offset = len(self.mods) - (self.height - 1)

        self.window.refresh(scroll_offset,
                            0,
                            self.y_offset,
                            self.x_offset,
                            self.height,
                            self.width)

    def hovered_mod(self):
        if(len(self.mods) > 0):
            return self.mods[self.scroll_position]
        else:
            return None

    def remove_selected(self):
        self.mods.remove(self.hovered_mod())


class TinkererApp:
    def __init__(self):
        # Monitor setup
        self.screen = curses.initscr()  # Initialize standard out
        self.screen.scrollok(True)      # Enable window scroll
        self.screen.keypad(True)        # Enable special key input
        self.screen.nodelay(True)       # Disable user-input blocking
        self.running = True

        # UI + Input Things
        self.selected_pane = 0

        # Modpack things
        self.modpack = None

        # Curses configuration
        curses.savetty()        # Save the terminal state
        curses.raw()            # Enable raw input (DISABLES SIGNALS)
        curses.noecho()         # Disable user-input echo
        curses.cbreak()         # Disable line-buffering (less input delay)
        curses.curs_set(False)  # Disable the cursor display

        # Curses colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    def start(self):
        # Fetch all available pack configs
        packs = TinkererApp.fetch_configs()

        # Build the mod registry
        self.registry = registry.Registry(packs)

        # Select the pack to work with
        selection_window = SelectionWindow(self.screen,
                                           packs,
                                           banner='Select A Pack')
        self.config_filename = selection_window.start()
        self.modpack = TinkererApp.load_config(self.config_filename)

        self.mod_pack_info_pane = ModPackInfoPane(self.screen)
        self.mod_info_pane = ModInfoPane(self.screen)
        self.mods_pane = ModsPane(self.screen, self.modpack.sorted_mods())

        while self.running:
            # Determine banner stuff
            banner = '[{}] {}'.format(time.ctime(), tinkerer.APP_NAME)
            info = '<F1:Info>-<F2:Controls>'
            _, pwidth = self.screen.getmaxyx()
            b_off = int((pwidth - len(banner)) / 2)

            # Get user input
            self.read_input()

            # Draw the screen
            self.screen.box()
            self.screen.addstr(0, 1, info)
            self.screen.addstr(0, b_off, banner)

            # Refresh
            self.screen.refresh()
            self.mod_pack_info_pane.draw(self.modpack)
            self.mods_pane.draw()
            self.mod_info_pane.draw(self.mods_pane.hovered_mod())
            time.sleep(0.1)
        self.stop()

    def stop(self):
        curses.nocbreak()           # Re-enable line-buffering
        curses.echo()               # Enable user-input echo
        curses.curs_set(True)       # Enable the cursor
        curses.resetty()            # Restore the terminal state
        curses.endwin()             # Destroy the virtual screen

    def read_input(self):
        # Grab new user input and immediately flush the buffer
        key = self.screen.getch()
        curses.flushinp()

        # Determine the key input
        if(key == curses.KEY_RESIZE):
            pheight, pwidth = self.screen.getmaxyx()
            self.screen.resize(pheight, pwidth)
            self.screen.clear()
            self.mod_pack_info_pane.resize()
            self.mod_info_pane.resize()
            self.mods_pane.resize()
        elif(key == curses.KEY_SLEFT):
            self.selected_pane -= 1
            self.update_selected_panel()
        elif(key == curses.KEY_SRIGHT):
            self.selected_pane += 1
            self.update_selected_panel()
        elif(key == curses.KEY_F1):
            window_message = '\n'.join(['Author: ' + tinkerer.APP_AUTHOR,
                                        'Website: ' + tinkerer.APP_WEBSITE,
                                        'License: ' + tinkerer.APP_LICENSE,
                                        'Version: ' + tinkerer.APP_VERSION])
            PopupWindow(self.screen,
                        window_message,
                        banner='About ' + tinkerer.APP_NAME,
                        color_pair=1)
        elif(key == curses.KEY_F2):
            PopupWindow(self.screen, "<Ctrl+C>: Exit program\
                                     \n\nInfo:\
                                     \n\t<F1>: About\
                                     \n\t<F2>: Controls\
                                     \n\nMovement:\
                                     \n\t<UP>: Scroll up\
                                     \n\t<DOWN>: Scroll down",
                        banner='Controls',
                        color_pair=1)
        elif(key == curses.KEY_F3):
            input = SelectionWindow(self.screen,
                                    ['Mod from Registry', 'New mod'],
                                    banner='How would you like ot add a mod?')
            method = input.start()
            method = {
                'Mod from Registry': 0,
                'New mod': 1
            }[method]
            if(method == 0):
                return
            else:
                new_mod = self.create_new_mod()
            self.modpack.add(new_mod)
            self.mods_pane.mods.append(new_mod)
            self.mods_pane.resize()
        elif(key == curses.KEY_F4):
            selected_mod = self.mods_pane.hovered_mod()
            if(selected_mod is not None):
                self.modpack.remove(selected_mod)
                self.mods_pane.remove_selected()
                self.mods_pane.resize()
        elif(key == curses.KEY_F5):
            input_window = InputWindow(self.screen,
                                       banner='Edit Name:',
                                       color_pair=2)
            selected_mod = self.mods_pane.hovered_mod()
            new_name = input_window.start()
            selected_mod.name = new_name
            self.mods_pane.resize()
        elif(key == curses.KEY_F6):
            input_window = InputWindow(self.screen,
                                       banner='Edit Project ID:',
                                       color_pair=2)
            selected_mod = self.mods_pane.hovered_mod()
            new_project_id = int(input_window
                                 .start(validator=InputWindow.is_numeric))
            selected_mod.project_id = new_project_id
        elif(key == curses.KEY_F7):
            input_window = InputWindow(self.screen,
                                       banner='Edit File ID:',
                                       color_pair=2)
            selected_mod = self.mods_pane.hovered_mod()
            new_file_id = int(input_window
                              .start(validator=InputWindow.is_numeric))
            selected_mod.file_id = new_file_id
        elif(key == curses.KEY_F8):
            input_window = SelectionWindow(self.screen,
                                           ['true', 'false'],
                                           banner='Required?',
                                           color_pair=2)
            selected_mod = self.mods_pane.hovered_mod()
            required = input_window.start()
            required = {
                'true': True,
                'false': False
            }[required]
            selected_mod.required = required
        elif(key == ord('c')):
            self.save_config()
        if(self.selected_pane == 0):
            self.mod_pack_info_pane.read_input(key)
        else:
            self.mods_pane.read_input(key)

    def update_selected_panel(self):
        if(self.selected_pane < 0):
            self.selected_pane = 0
        elif(self.selected_pane >= 2):
            self.selected_pane = 1

        if(self.selected_pane == 0):
            self.mods_pane.selected = False
            self.mod_pack_info_pane.selected = True
        else:
            self.mods_pane.selected = True
            self.mod_pack_info_pane.selected = False
        self.mods_pane.resize()
        self.mod_pack_info_pane.resize()

    def create_new_mod(self) -> mod.Mod:
        input_window = InputWindow(self.screen,
                                   banner='New Mod: Mod Name',
                                   color_pair=2)
        name = input_window.start()
        input_window = InputWindow(self.screen,
                                   banner='New Mod: Project ID',
                                   color_pair=2)
        project_id = int(input_window
                         .start(validator=InputWindow.is_numeric))
        input_window = InputWindow(self.screen,
                                   banner='New Mod: File ID',
                                   color_pair=2)
        file_id = int(input_window
                      .start(validator=InputWindow.is_numeric))
        input_window = SelectionWindow(self.screen,
                                       ['true', 'false'],
                                       banner='New Mod: Required?:',
                                       color_pair=2)
        required = input_window.start()
        required = {
            'true': True,
            'false': False
        }[required]
        return mod.Mod(name, project_id, file_id, required)

    def fetch_configs() -> [str]:
        return os.listdir(path=tinkerer.MC_PACKS_DIR)

    def load_config(filename: str) -> modpack.ModPack:
        with open(tinkerer.MC_PACKS_DIR + filename) as file:
            return modpack.ModPack.to_modpack(json.load(file))

    def save_config(self) -> None:
        file_content = json.dumps(self.modpack.to_dict(),
                                  skipkeys=True,
                                  allow_nan=True,
                                  indent=2,
                                  sort_keys=True)

        file = open(tinkerer.MC_PACKS_DIR + self.config_filename, 'w+')
        file.write('{}\n'.format(file_content))
        file.close()
        self.running = False
