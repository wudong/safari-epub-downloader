from pathlib import Path

from epubgen.EpubManager import EpubManager
from epubgen.SafariBook import SafariBook;
from epubgen.SafariApi import SafariApi
from epubgen.SafariBookResourceDownloader import SafariBookResourceDownloader

import argparse
import logging

from epubgen.job import Identity


class Main:
    def __init__(self, identity: Identity, work_dir="work"):
        self.work_dir = work_dir
        self.identity = identity
        self.api = SafariApi(self.identity)
        self.downloader = SafariBookResourceDownloader(self.api)
        self.api.do_login()

    def retrieve_epub(self, book_id):
        logging.info(f"To download book id: {book_id}")
        
        working_path = "{}/{}".format(self.work_dir, book_id)        
        logging.info(f"Save to: {working_path}")
        
        path = Path(working_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        self.downloader.download(working_path, book_id)
        logging.info(f"Finished downloading book content of {book_id}")

    def create_epub(self, book_id):
        working_path = "{}/{}".format(self.work_dir, book_id)
        safari_book = SafariBook.from_json_file_from_work_dir(working_path)
        EpubManager(safari_book).create_epub(self.work_dir)
        logging.info(f"Epub book created for {book_id}")


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
    downloader = Main(identity)
    
    for book_id in args['bookids']:
        downloader.retrieve_epub(book_id)
        downloader.create_epub(book_id)

            
if __name__ == "__main__":
    main()
