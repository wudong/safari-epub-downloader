import argparse
import logging

from epubgen.Facade import Facade, Identity


def parse_args():
    parser = argparse.ArgumentParser(description='Epub Downloader for Safari')
    parser.add_argument('--username', nargs=1, help='user email of safari online')
    parser.add_argument('--password', nargs=1, help='password of safari online')
    parser.add_argument('bookids', nargs="+", help='the list of bookid that to be downloaded')
    return vars(parser.parse_args())


def main():
    logging.basicConfig(level=logging.INFO)

    args = parse_args()
    identity = Identity(args["username"], args["password"])
    facade = Facade(identity)

    for book_id in args['bookids']:
        facade.retrieve_epub(book_id)
        facade.create_epub(book_id)


if __name__ == "__main__":
    main()
