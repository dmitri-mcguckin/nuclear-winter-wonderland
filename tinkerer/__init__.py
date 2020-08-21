import os
MAJOR = 3
MINOR = 0
PATCH = 0

APP_NAME = 'Tinkerer'
APP_AUTHOR = 'Dmitri McGuckin'
APP_WEBSITE = 'https://github.com/dmitri-mcguckin/tinkerer'
APP_LICENSE = 'MIT'
APP_VERSION = "{}.{}.{}".format(MAJOR, MINOR, PATCH)
APP_DIRECTORY = os.path.expanduser('~/.config/tinkerer')
MC_PACKS_DIR = APP_DIRECTORY + os.sep + 'mc-packs' + os.sep

DEBUG = False
