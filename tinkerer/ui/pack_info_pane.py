import curses
import tinkerer.modpack as modpack
from tinkerer.ui.sub_windows import PopupWindow, \
                                    InputWindow


class PackInfoPane:
    def __init__(self, parent, pack: modpack.ModPack):
        self.parent = parent
        self.window = curses.newpad(1, 1)
        self.pack = pack
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
        self.x_offset = 1
        self.y_offset = 1

        self.window.resize(self.height, self.width)
        self.window.clear()

    def draw(self, pack: modpack.ModPack):
        self.window.box()

        if(self.selected):
            self.window.attron(curses.A_REVERSE)
        self.window.addstr(0, 1, 'Pack-Details:')
        self.window.attroff(curses.A_REVERSE)

        entries = [
            pack.name,
            '\tBy: {}'.format(pack.author),
            '\tPack Version: {}'.format(pack.pack_version),
            '\tMC Version: {}'.format(pack.mc_version),
            '\tForge Version: {}'.format(pack.forge_version.long()),
            '\tSponge Version: {}'.format(pack.sponge_version)
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
            self.modify_pack()
        if(self.scroll_pos < 0):
            self.scroll_pos = 0
        elif(self.scroll_pos > 5):
            self.scroll_pos = 5

    def modify_pack(self):
        if(self.scroll_pos == 0):
            self.edit_name()
        elif(self.scroll_pos == 1):
            self.edit_author()
        elif(self.scroll_pos == 2):
            self.edit_pack_version()
        elif(self.scroll_pos == 3):
            self.edit_mc_version()
        elif(self.scroll_pos == 4):
            self.edit_forge_version()
        elif(self.scroll_pos == 5):
            self.edit_sponge_version()
        self.resize()

    def edit_name(self):
        input = InputWindow(self.parent,
                            banner='Edit Pack: Name',
                            color_pair=2)
        new_name = input.start()
        if(new_name != ''):
            self.pack.name = new_name
        else:
            PopupWindow(self.parent, 'Name cannot be empty!')

    def edit_author(self):
        input = InputWindow(self.parent,
                            banner='Edit Pack: Author',
                            color_pair=2)
        new_author = input.start()
        if(new_author != ''):
            self.pack.author = new_author
        else:
            PopupWindow(self.parent, 'Author cannot be empty!')

    def edit_pack_version(self):
        input = InputWindow(self.parent,
                            banner='Edit Pack: Version',
                            color_pair=2)
        new_pack_version = input.start()
        try:
            self.pack.pack_version = modpack.Version \
                                            .to_version(new_pack_version)
        except Exception:
            PopupWindow(self.parent, 'Pack Version cannot be empty and must look like:\n\txx.xx.xx')

    def edit_mc_version(self):
        input = InputWindow(self.parent,
                            banner='Edit Pack: MC Version',
                            color_pair=2)
        new_mc_version = input.start()
        try:
            self.pack.mc_version = modpack.Version.to_version(new_mc_version)
        except Exception:
            PopupWindow(self.parent, 'MC Version cannot be empty and must look like:\n\txx.xx.xx')

    def edit_forge_version(self):
        input = InputWindow(self.parent,
                            banner='Edit Pack: Forge Version',
                            color_pair=2)
        new_forge_version = input.start()

        # Add the forge tag if the user forgot it
        if('forge-' not in new_forge_version):
            new_forge_version = 'forge-{}'.format(new_forge_version)

        try:
            self.pack.forge_version = modpack \
                                        .ForgeVersion \
                                        .to_version('forge-' + new_forge_version)
        except Exception:
            PopupWindow(self.parent, 'Forge Version cannot be empty and must look like:\n\txx.xx.x.xxxx\n\tor\n\tforge-xx.xx.x.xxxx')

    def edit_sponge_version(self):
        input = InputWindow(self.parent,
                            banner='Edit Pack: Sponge Version',
                            color_pair=2)
        new_sponge_version = input.start()
        if(new_sponge_version != ''):
            try:
                self.pack.sponge_version = modpack \
                                            .Version \
                                            .to_version(new_sponge_version)
            except Exception:
                PopupWindow(self.parent, 'Sponge Version must look like:\n\txx.xx.xx')
        else:
            self.pack.sponge_version = None
