import time
import curses
import tinkerer
import tinkerer.registry as registry
from tinkerer.builder import Builder
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
        self.dirty_changes = False

        # UI + Input Things
        self.selected_pane = 0

        # Modpack things
        self.modpack = None
        self.builder = None

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
        packs = Builder.fetch_configs()

        # Build the mod registry
        self.registry = registry.Registry(packs)

        # Select the pack to work with
        selection_window = SelectionWindow(self.screen,
                                           packs,
                                           banner='Select A Pack')
        self.config_filename = selection_window.start()
        self.modpack = Builder.load_config(self.config_filename)

        self.pack_info_pane = PackInfoPane(self.screen, self.modpack)
        self.mod_info_pane = ModInfoPane(self.screen, self.modpack)
        self.mod_list_pane = ModListPane(self.screen, self.modpack)

        while self.running:
            # Determine banner stuff
            if(self.dirty_changes):
                commited = '<Unsaved changes>'
            else:
                commited = ''

            banner = '[{}] {} {}'.format(time.ctime(),
                                         tinkerer.APP_NAME,
                                         commited)
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
                                     \n\t<Ctrl+UP>: Scroll up by 10\
                                     \n\t<Ctrl+DOWN>: Scroll down by 10\
                                     \n\t<Shift+UP/Shift+LEFT>: Select previous pane\
                                     \n\t<Shift+DOWN/Shift+RIGHT>: Select next pane",
                        banner='Controls',
                        color_pair=1)
        elif(key == ord('s')):
            self.save_modpack_as()
        elif(key == ord('C')):
            self.build_client()
        elif(key == ord('S')):
            self.build_server()

        # Delegate input-reading to sub-panes
        if(self.selected_pane == 0):
            action = self.pack_info_pane.read_input(key)
        elif(self.selected_pane == 1):
            action = self.mod_info_pane.read_input(key, self.mod_list_pane
                                                            .hovered_mod())
        elif(self.selected_pane == 2):
            action = self.mod_list_pane.read_input(key)

        if(action == 1):  # If anything got updated, then data is uncommited
            self.dirty_changes = True
        if(action == 2):  # If a mod was removed, revresh the mod list pane
            self.dirty_changes = True
            self.mod_list_pane.scroll_position -= 1
            self.mod_list_pane.resize()

    def save_modpack(self):
        Builder.save_config(self.config_filename, self.modpack)
        self.dirty_changes = False

    def save_modpack_as(self):
        # input = InputWindow(self.screen, banner='Save Config As:')
        new_filename = self.modpack.name

        if(new_filename != ''):
            if('.json' not in new_filename):
                new_filename += '.json'
            new_filename = new_filename.strip() \
                                       .replace(' ', '-') \
                                       .lower()
            self.config_filename = new_filename
            self.save_modpack()
        else:
            PopupWindow(self.screen, 'Filename cannot be blank!')

    def build_client(self):
        self.builder = Builder(self.config_filename, self.modpack)
        client_path = self.builder.build_client()
        PopupWindow(self.screen, 'Client succesfully built!\nSaved to: {}'
                                 .format(client_path), color_pair=1)

    def build_server(self):
        if(self.builder is None):
            self.builder = Builder(self.config_filename, self.modpack)

        try:
            server_path = self.builder.build_server()
            PopupWindow(self.screen, 'Server succesfully built!\nSaved to: {}'
                                     .format(server_path), color_pair=1)
        except Exception as e:
            PopupWindow(self.screen, str(e))

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
