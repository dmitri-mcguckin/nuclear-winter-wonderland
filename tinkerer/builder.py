import os
import json
import wget
import shutil
import zipfile
import tinkerer
import tinkerer.modpack as modpack
import tinkerer.conf_parser as conf_parser


class Builder:
    def __init__(self, config_filename: str, pack: modpack.ModPack):
        self.pack = pack
        self.config_filename = config_filename
        self.package_name = self.config_filename.split('.json')[0]
        self.client_path = '{}{}-{}'.format(tinkerer.MC_HOME,
                                            self.package_name,
                                            self.pack.pack_version)

    def fetch_configs() -> [str]:
        files = os.listdir(path=tinkerer.MC_PACKS_DIR)
        return list(filter(lambda x: '.json' in x, files))

    def load_config(filename: str) -> modpack.ModPack:
        with open(tinkerer.MC_PACKS_DIR + filename) as file:
            return modpack.ModPack.to_modpack(json.load(file))

    def save_config(filename: str, pack: modpack.ModPack) -> None:
        file_content = json.dumps(pack.to_dict(),
                                  skipkeys=True,
                                  allow_nan=True,
                                  indent=2,
                                  sort_keys=True)

        file = open(tinkerer.MC_PACKS_DIR + filename, 'w+')
        file.write('{}\n'.format(file_content))
        file.close()

    def zip_directory(path: str, zipper: zipfile.ZipFile) -> None:
        for root, dirs, files in os.walk(path):
            for file in files:
                filename = os.path.join(root, file)
                arcname = '/'.join(filename.split('/')[6:])
                zipper.write(filename, arcname=arcname)

    def client_is_built(self):
        return os.path.exists(self.client_path)

    def setup_staging(self) -> None:
        self.teardown_staging()
        os.makedirs(tinkerer.STAGING_DIR, exist_ok=True)
        os.makedirs(tinkerer.BUILDS_DIR, exist_ok=True)

    def teardown_staging(self):
        shutil.rmtree(tinkerer.STAGING_DIR, ignore_errors=True)

    def build_client(self) -> str:
        # Determine the package name
        client_zip = '{}{}-{}.zip'.format(tinkerer.BUILDS_DIR,
                                          self.package_name,
                                          str(self.pack.pack_version))

        # Setup the staging directory
        self.setup_staging()

        # Copy the manifest config
        shutil.copyfile(tinkerer.MC_PACKS_DIR + self.config_filename,
                        tinkerer.STAGING_DIR + 'manifest.json')

        # Copy the config overrides
        shutil.copytree(tinkerer.OVERRIDES_DIR,
                        tinkerer.STAGING_DIR + 'overrides')

        # Package the client
        zipper = zipfile.ZipFile(client_zip,
                                 'w',
                                 zipfile.ZIP_DEFLATED,
                                 compresslevel=9)
        Builder.zip_directory(tinkerer.STAGING_DIR, zipper)
        zipper.close()

        # Teardown staging
        self.teardown_staging()
        return client_zip

    def build_server(self) -> str:
        if(not self.client_is_built()):
            raise OSError('The client for {} has not been built yet!'.format(self.client_path))

        # Determine the package name
        server_zip = '{}{}-{}-server.zip'.format(tinkerer.BUILDS_DIR,
                                                 self.package_name,
                                                 str(self.pack.pack_version))

        # Setup the staging directory
        self.setup_staging()

        # Copy the manifest config
        shutil.copyfile(tinkerer.MC_PACKS_DIR + self.config_filename,
                        tinkerer.STAGING_DIR + 'manifest.json')

        ##
        # server.properties
        ##
        # Load
        sp_path = tinkerer.RESOURCES_DIR + 'server.properties'
        file = open(sp_path, 'r')
        properties = conf_parser.parse(file.read())
        file.close()

        # Update data
        properties['motd'] = ' | '.join([
            self.pack.name,
            str(self.pack.pack_version),
            str(self.pack.mc_version),
            self.pack.forge_version.long()
        ])

        # Save to staging
        sp_path = tinkerer.STAGING_DIR + 'server.properties'
        file = open(sp_path, 'w')
        file.write(conf_parser.dumps(properties))
        file.close()

        ##
        # resources.properties
        ##
        # Load
        rp_path = tinkerer.RESOURCES_DIR + 'resources.properties'
        file = open(rp_path, 'r')
        resources = conf_parser.parse(file.read())
        file.close()

        # Update data
        resources['mc-version'] = self.pack.mc_version
        resources['forge-version'] = self.pack.forge_version.medium()

        # Save to staging
        rp_path = tinkerer.STAGING_DIR + 'resources.sh'
        file = open(rp_path, 'w')
        file.write(conf_parser.dumps_shell(resources))
        file.close()

        # Copy the manifest config
        shutil.copyfile(tinkerer.MC_PACKS_DIR + self.config_filename,
                        tinkerer.STAGING_DIR + 'manifest.json')

        # Copy the configs
        shutil.copytree(tinkerer.OVERRIDES_DIR,
                        tinkerer.STAGING_DIR
                        + os.sep
                        + 'config')

        # Copy the start script
        shutil.copyfile(tinkerer.RESOURCES_DIR + 'start.sh',
                        tinkerer.STAGING_DIR + 'start.sh')

        # Copy the built mods directory into staging
        built_mods_dir = self.client_path \
            + os.sep \
            + 'minecraft' \
            + os.sep \
            + 'mods'
        shutil.copytree(built_mods_dir, tinkerer.STAGING_DIR + os.sep + 'mods')

        # Install forge
        jar_name = 'forge-{}-{}-installer.jar' \
                   .format(self.pack.mc_version,
                           self.pack.forge_version.medium())
        uri = tinkerer.FORGE_URI.format(self.pack.mc_version,
                                        self.pack.forge_version.medium(),
                                        jar_name)
        local_jar = wget.download(uri)
        shutil.move(local_jar, tinkerer.STAGING_DIR)
        working_dir = os.getcwd()
        os.chdir(tinkerer.STAGING_DIR)
        os.system('java -jar ' + local_jar + ' --installServer')

        # Post forge install cleanup
        os.remove(local_jar)
        os.chdir(working_dir)

        # Package the server
        zipper = zipfile.ZipFile(server_zip,
                                 'w',
                                 zipfile.ZIP_DEFLATED,
                                 compresslevel=9)
        Builder.zip_directory(tinkerer.STAGING_DIR, zipper)
        zipper.close()

        # Teardown staging
        self.teardown_staging()
        return server_zip
