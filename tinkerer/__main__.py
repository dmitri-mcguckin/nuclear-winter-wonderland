import sys
import argparse
import tinkerer
import tinkerer.tinkerer_app as tapp


def main(args):
    parser = argparse.ArgumentParser(
                        prog=tinkerer.APP_NAME,
                        description=tinkerer.APP_DESCRIPTION,
                        allow_abbrev=False)
    parser.add_argument('-v', '--verbose',
                        dest='debug',
                        action='store_true')
    args = parser.parse_args(args)

    tinkerer.DEBUG = args.debug

    app = tapp.TinkererApp()
    try:
        app.start()
    except KeyboardInterrupt:
        print('Stopping tinkerer...')
    finally:
        app.stop()
        print('Goodbye!')


if __name__ == '__main__':
    main(sys.argv[1:])
