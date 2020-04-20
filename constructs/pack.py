ATTRS = ['name', 'pack_version', 'mc_version', 'forge_version', 'author']

class Version:
    def __init__(self, major, minor, patch):
        self.major = major
        self.minor = minor
        self.patch = patch

    def __eq__(self, ver):
        return (self.major == ver.major and self.minor == ver.minor and self.patch == ver.patch)

    def __str__(self):
        return str(self.major) + "." + str(self.minor) + "." + str(self.patch)

class ForgeVersion(Version):
    def __init__(self, major, minor, patch, forge):
        super().__init__(major, minor, patch)
        self.forge = forge

    def bannerless_str(self):
        return str(self.major) \
                + "." + str(self.minor) \
                + "." + str(self.patch) \
                + "." + str(self.forge)

    def __str__(self):
        return "forge-" + self.bannerless_str()

class Pack:
    def __init__(self, name, pack_version, mc_version, forge_version, author, sponge_version = None):
        self.name = name
        self.pack_version = pack_version
        self.mc_version = mc_version
        self.forge_version = forge_version
        self.author = author
        self.sponge_version = sponge_version
        self.mods = []

    def add(self, mod): self.mods.append(mod)

    def __eq__(self, pack):
        return (self.name == pack.name) \
                and (self.pack_version == pack.pack_version) \
                and (self.mc_version == pack.mc_version) \
                and (self.forge_version == pack.forge_version)

    def alphabetical_mod_list(self):
        if(len(self.mods) > 0): return sorted(self.mods, key = lambda x: x.name)
        return []

    def to_dict(self):
        if(self.sponge_version is not None): sv = str(self.sponge_version)
        else: sv = self.sponge_version

        res = { "minecraft": {
                    "version": str(self.mc_version),
                    "modLoaders": [ { "id": str(self.forge_version), "primary": True } ]
                },
            "manifestType": "minecraftModpack",
            "manifestVersion": 1,
            "name": self.name,
            "version": str(self.pack_version),
            "author": self.author,
            "sponge_version": sv,
            "files": [],
            "overrides": "overrides" }

        for mod in self.mods: res['files'].append(mod.to_dict())
        return res

    def __len__(self): return len(self.mods)

    def __str__(self):
        res = self.name + " v" + str(self.pack_version) \
            + ", MC " + str(self.mc_version) \
            + ", Forge " + str(self.forge_version) \
            + " by " + self.author \
            + "\n\tMods (" + str(len(self.mods)) + "):"
        for mod in self.mods: res += "\n\t" + str(mod)
        return res
