import re
import curses
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
        # parent.refresh()

        window.getch()
        curses.flushinp()
        window.clear()
        parent.clear()


class SelectionWindow:
    def __init__(self, parent, options, banner='Select One', color_pair=3):
        height, width = parent.getmaxyx()

        long = len(banner)

        for m in options:
            if(len(str(m)) > long):
                long = len(str(m))
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
                option = str(option).split('.')[0].replace('-', ' ').title()
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

        # Do bounds checking on option hovering
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

    # Alphanumeric Validator
    def is_numeric(key) -> chr:
        search = re.match('[0-9]', chr(key))

        if(search is not None):
            return search.string
        elif(key == 10):
            return key
        else:
            return None
