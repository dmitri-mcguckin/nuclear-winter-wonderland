from tinkerer.builder import Builder
import tinkerer.mod as mod


class Registry:
    def __init__(self, configs: [str]):
        self.mods: {int: mod.Mod} = {}

        for config in configs:
            pack = Builder.load_config(config)
            for m in pack.mods:
                self.mods[m.project_id] = m

    def registered_mods(self) -> [str]:
        if(len(self.mods) > 0):
            return list(map(lambda x: x.name, self.mods.values()))
        else:
            return None
