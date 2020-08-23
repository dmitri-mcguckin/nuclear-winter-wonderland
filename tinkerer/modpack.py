import tinkerer.mod as mod


class Version:
    def __init__(self, major, minor, patch):
        self.major = major
        self.minor = minor
        self.patch = patch

    def __eq__(self, ver) -> str:
        return (self.major == ver.major
                and self.minor == ver.minor
                and self.patch == ver.patch)

    def __str__(self) -> str:
        return "{}.{}.{}".format(self.major,
                                 self.minor,
                                 self.patch)

    def to_version(data: str):
        pieces = data.split('.')
        return Version(int(pieces[0]), int(pieces[1]), int(pieces[2]))


class ForgeVersion(Version):
    def __init__(self, major, minor, patch, forge):
        super().__init__(major, minor, patch)
        self.forge = forge

    def short(self) -> str:
        return super().__str__()

    def medium(self):
        return "{}.{}".format(super().__str__(), self.forge)

    def long(self):
        return "forge-{}.{}".format(super().__str__(), self.forge)

    def __eq__(self, ver):
        return super().__eq__(ver) and self.forge == ver.forge

    def __repr__(self):
        return "<Forge {}.{}.{}.{}>".format(self.major,
                                            self.minor,
                                            self.patch,
                                            self.forge)

    def to_version(data: str):
        pieces = data.split('forge-')[1].split('.')
        return ForgeVersion(int(pieces[0]),
                            int(pieces[1]),
                            int(pieces[2]),
                            int(pieces[3]))


class ModPack:
    def __init__(self,
                 name: str,
                 pack_version: Version,
                 mc_version: Version,
                 forge_version: ForgeVersion,
                 author: str,
                 sponge_version: Version = None):
        self.name = name
        self.pack_version = pack_version
        self.mc_version = mc_version
        self.forge_version = forge_version
        self.author = author
        self.sponge_version = sponge_version
        self.mods = []

    def add(self, mod: mod.Mod) -> None:
        self.mods.append(mod)

    def remove(self, mod: mod.Mod):
        self.mods.remove(mod)

    def __eq__(self, pack) -> bool:
        return (self.name == pack.name) \
                and (self.pack_version == pack.pack_version) \
                and (self.mc_version == pack.mc_version) \
                and (self.forge_version == pack.forge_version)

    def __getitem__(self, index):
        return self.sorted_mods()[index]

    def sorted_mods(self) -> [mod.Mod]:
        if(len(self.mods) > 0):
            return sorted(self.mods, key=lambda x: x.name)
        return []

    def to_dict(self) -> dict:
        if(self.sponge_version is None):
            sv = None
        else:
            sv = str(self.sponge_version)
        res = {"minecraft": {"version": str(self.mc_version),
                             "modLoaders": [{"id": self.forge_version.long(),
                                            "primary": True}]},
               "manifestType": "minecraftModpack",
               "manifestVersion": 1,
               "name": self.name,
               "version": str(self.pack_version),
               "author": self.author,
               "sponge_version": sv,
               "files": [],
               "overrides": "overrides"}

        for m in self.mods:
            res['files'].append(m.to_dict())
        return res

    def to_modpack(data: dict):
        name = data['name']
        pack_version = Version.to_version(data['version'])
        mc_version = Version.to_version(data['minecraft']['version'])
        forge_version = ForgeVersion.to_version(data['minecraft']
                                                    ['modLoaders']
                                                    [0]
                                                    ['id'])
        author = data['author']
        sponge_version = data.get('sponge_version')

        if(sponge_version is not None):
            sponge_version = Version.to_version(data['sponge_version'])

        modpack = ModPack(name,
                          pack_version,
                          mc_version,
                          forge_version,
                          author,
                          sponge_version)

        for file in data.get('files'):
            modpack.add(mod.Mod.to_mod(file))
        return modpack

    def __len__(self) -> int:
        return len(self.mods)

    def __str__(self) -> str:
        return "<ModPack {} (ver: {}) (forge: {}) ({} mods)>" \
                    .format(self.name,
                            self.pack_version,
                            self.forge_version.long(),
                            len(self.mods))
