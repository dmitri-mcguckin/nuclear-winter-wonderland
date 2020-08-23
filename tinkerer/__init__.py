import os

MAJOR = 4
MINOR = 0
PATCH = 0

APP_NAME = 'mc-tinkerer'
APP_AUTHOR = 'Dmitri McGuckin'
APP_EMAIL = 'dmitri@mandatoryfun.xyz'
APP_DESCRIPTION = 'An MC Modpack builder, an alternative to both the twitch\
                   client pack editor and editing manifest jsons manually.'
APP_URL = 'https://github.com/dmitri-mcguckin/tinkerer'
APP_LICENSE = 'MIT'
APP_VERSION = "{}.{}.{}".format(MAJOR, MINOR, PATCH)

APP_DIRECTORY = os.path.expanduser('~/.config/tinkerer')
MC_HOME = os.getenv('MC_HOME') + os.sep

BUILDS_DIR = APP_DIRECTORY + os.sep + 'build' + os.sep
MC_PACKS_DIR = APP_DIRECTORY + os.sep + 'mc-packs' + os.sep
OVERRIDES_DIR = APP_DIRECTORY + os.sep + 'overrides' + os.sep
RESOURCES_DIR = APP_DIRECTORY + os.sep + 'resources' + os.sep
STAGING_DIR = APP_DIRECTORY + os.sep + 'staging' + os.sep

DEBUG = False


FORGE_URI = 'https://files.minecraftforge.net/maven/net/minecraftforge/forge/{}-{}/{}'
# + str(pack.mc_version) + '-' + pack.forge_version.bannerless_str() + os.sep + forge_jar
