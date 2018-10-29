import uuid
from pathlib import Path

from epubgen.EpubManager import EpubManager
from epubgen.SafariBook import SafariBook;
from epubgen.SafariApi import SafariApi
from epubgen.ResourceDownloader import SafariBookResourceDownloader

import logging


class Identity:
    def __init__(self, username, password):
        self.user_name = username
        self.password = password
        self.cookie = {}
        self.logged_in = False
        self.id = f"uid_{uuid.uuid4()}"

    def get_username(self):
        return self.user_name

    def get_password(self):
        return self.password

    def get_identity(self):
        return self.cookie

    def log_in(self):
        self.logged_in = True

    def is_logged_in(self):
        return self.logged_in

    def get_cookie(self):
        return self.cookie

    def get_id(self):
        return self.id


class Facade:
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
