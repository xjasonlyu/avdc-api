import argparse
import os

from werkzeug.serving import run_simple

from server import app


def parse_arguments():
    parser = argparse.ArgumentParser(prog='avdc-api')

    parser.add_argument('-b', '--bind', type=str, default='0.0.0.0',
                        help='host to serve [Default=0.0.0.0]')
    parser.add_argument('-p', '--port', type=int, default=5000,
                        help='port to serve [Default=5000]')
    parser.add_argument('-d', '--db-url', type=str, default='sqlite:///:memory:',
                        help='database url to load [Default=sqlite:///:memory:]')
    parser.add_argument('-t', '--token', type=str, help='token for avdc api')
    parser.add_argument('--debug', action='store_true',
                        help='enable debug mode')

    return parser.parse_args()


def main():
    args = parse_arguments()

    app.config.update(TOKEN=os.environ.get('AVDC_TOKEN') or args.token)
    app.config.update(DBURL=os.environ.get('AVDC_DBURL') or args.db_url)

    run_simple(hostname=args.bind,
               port=args.port,
               application=app,
               threaded=True,
               use_debugger=args.debug,
               use_reloader=args.debug)


if __name__ == '__main__':
    main()
