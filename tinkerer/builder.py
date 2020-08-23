import os
import json
import tinkerer
import tinkerer.modpack as modpack


class Builder:
    def __init__(self):
        pass

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
