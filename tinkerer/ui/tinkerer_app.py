import time
import curses
import tinkerer
import tinkerer.mod as mod
import tinkerer.builder as builder
import tinkerer.registry as registry
from tinkerer.ui.pack_info_pane import PackInfoPane
from tinkerer.ui.mod_info_pane import ModInfoPane
from tinkerer.ui.mod_list_pane import ModListPane
from tinkerer.ui.sub_windows import PopupWindow, \
                                    SelectionWindow, \
                                    InputWindow


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
        packs = builder.Builder.fetch_configs()

        # Build the mod registry
        self.registry = registry.Registry(packs)

        # Select the pack to work with
        selection_window = SelectionWindow(self.screen,
                                           packs,
                                           banner='Select A Pack')
        self.config_filename = selection_window.start()
        self.modpack = builder.Builder.load_config(self.config_filename)

        self.pack_info_pane = PackInfoPane(self.screen, self.modpack)
        self.mod_info_pane = ModInfoPane(self.screen, self.modpack)
        self.mod_list_pane = ModListPane(self.screen, self.modpack)

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
            self.pack_info_pane.draw(self.modpack)
            self.mod_list_pane.draw()
            self.mod_info_pane.draw(self.mod_list_pane.hovered_mod())
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
            self.screen.clear()
            self.pack_info_pane.resize()
            self.mod_info_pane.resize()
            self.mod_list_pane.resize()
        elif(key == curses.KEY_SR or key == curses.KEY_SLEFT):
            self.selected_pane -= 1
            self.update_selected_panel()
        elif(key == curses.KEY_SF or key == curses.KEY_SRIGHT):
            self.selected_pane += 1
            self.update_selected_panel()
        elif(key == curses.KEY_F1):
            window_message = '\n'.join(['Version: ' + tinkerer.APP_VERSION,
                                        'Author: ' + tinkerer.APP_AUTHOR,
                                        'Website: ' + tinkerer.APP_URL,
                                        'License: ' + tinkerer.APP_LICENSE])
            PopupWindow(self.screen,
                        window_message,
                        banner='About ' + tinkerer.APP_NAME,
                        color_pair=1)
        elif(key == curses.KEY_F2):
            PopupWindow(self.screen, "<Ctrl+C>: Exit without saving\
                                     \n<S>: Save and exit\
                                     \n\nInfo:\
                                     \n\t<F1>: About\
                                     \n\t<F2>: Controls\
                                     \n\nMovement:\
                                     \n\t<ENTER>: Edit selected field\
                                     \n\t<UP>: Scroll up\
                                     \n\t<DOWN>: Scroll down\
                                     \n\t<Shift+UP/Shift+LEFT>: Select previous pane\
                                     \n\t<Shift+DOWN/Shift+RIGHT>: Select next pane",
                        banner='Controls',
                        color_pair=1)
        elif(key == ord('s') or key == ord('S')):
            self.save_config()
        if(self.selected_pane == 0):
            self.pack_info_pane.read_input(key)
        elif(self.selected_pane == 1):
            did_remove = self.mod_info_pane.read_input(key, self.mod_list_pane
                                                                .hovered_mod())

            # If a mod was removed, revresh the mod list pane
            if(did_remove):
                self.mod_list_pane.resize()
        elif(self.selected_pane == 2):
            self.mod_list_pane.read_input(key)

    def update_selected_panel(self):
        if(self.selected_pane < 0):
            self.selected_pane = 0
        elif(self.selected_pane > 2):
            self.selected_pane = 2

        self.mod_list_pane.selected = False
        self.mod_info_pane.selected = False
        self.pack_info_pane.selected = False

        if(self.selected_pane == 0):
            self.pack_info_pane.selected = True
        elif(self.selected_pane == 1):
            self.mod_info_pane.selected = True
        elif(self.selected_pane == 2):
            self.mod_list_pane.selected = True

        self.mod_list_pane.resize()
        self.mod_info_pane.resize()
        self.pack_info_pane.resize()

    def create_new_mod(self) -> mod.Mod:
        input_window = InputWindow(self.screen,
                                   banner='New Mod: Name',
                                   color_pair=2)
        name = input_window.start()
        input_window = InputWindow(self.screen,
                                   banner='New Mod: Project ID',
                                   color_pair=2)
        project_id = int(input_window.start(validator=InputWindow.is_numeric))
        input_window = InputWindow(self.screen,
                                   banner='New Mod: File ID',
                                   color_pair=2)
        file_id = int(input_window.start(validator=InputWindow.is_numeric))
        input_window = SelectionWindow(self.screen,
                                       [True, False],
                                       banner='New Mod: Required?:',
                                       color_pair=2)
        required = input_window.start()
        return mod.Mod(name, project_id, file_id, required)
