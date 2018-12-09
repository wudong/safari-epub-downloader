import argparse
import logging

from epubgen.Facade import Facade, Identity


def enable_http_debug():
    from http.client import HTTPConnection
    HTTPConnection.debuglevel = 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def parse_args():
    parser = argparse.ArgumentParser(description='Epub Downloader for Safari')
    parser.add_argument('--cookie', help='the cookie file that used to send request')
    parser.add_argument('bookids', nargs="+", help='the list of bookid that to be downloaded')
    return vars(parser.parse_args())


def main():
    logging.basicConfig(level=logging.INFO)

    args = parse_args()
    identity = Identity(args["cookie"])
    facade = Facade(identity)

    for book_id in args['bookids']:
        facade.retrieve_epub(book_id)
        facade.create_epub(book_id)


if __name__ == "__main__":
    main()
