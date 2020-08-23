import sys
import argparse
import tinkerer
from tinkerer.ui.tinkerer_app import TinkererApp


def main():
    parser = argparse.ArgumentParser(
                        prog=tinkerer.APP_NAME,
                        description=tinkerer.APP_DESCRIPTION,
                        allow_abbrev=False)
    parser.add_argument('-v', '--verbose',
                        dest='debug',
                        action='store_true',
                        default=False,
                        help='enables additional debug information')
    parser.add_argument('-V', '--version',
                        dest='version',
                        action='store_true',
                        help='outputs the app version and exits')
    args = parser.parse_args()

    if(args.version):
        print('{} v{}'.format(tinkerer.APP_NAME, tinkerer.APP_VERSION))
        sys.exit(0)

    tinkerer.DEBUG = args.debug

    app = TinkererApp()
    try:
        app.start()
    except KeyboardInterrupt:
        print('Stopping {}...'.format(tinkerer.APP_NAME))
    finally:
        app.stop()
        print('Goodbye!')


if __name__ == '__main__':
    main()
