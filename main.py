import argparse
import os

from werkzeug.serving import run_simple

from server import app


def parse_arguments():
    parser = argparse.ArgumentParser(prog='AVDC')

    parser.add_argument('-b', '--bind', type=str, default='0.0.0.0',
                        help='host to serve [Default=0.0.0.0]')
    parser.add_argument('-p', '--port', type=int, default=5000,
                        help='port to serve [Default=5000]')
    parser.add_argument('-d', '--database', type=str, default='avdc.db',
                        help='database to load [Default=avdc.db]')
    parser.add_argument('-t', '--token', type=str, help='token for avdc api')
    parser.add_argument('--debug', action='store_true',
                        help='enable debug mode')

    return parser.parse_args()


def main():
    args = parse_arguments()

    app.config.update(DATABASE=os.environ.get('AVDC_DB') or args.database)
    app.config.update(TOKEN=os.environ.get('AVDC_TOKEN') or args.token)

    run_simple(hostname=args.bind,
               port=args.port,
               application=app,
               threaded=True,
               use_debugger=args.debug,
               use_reloader=args.debug)


if __name__ == '__main__':
    main()
