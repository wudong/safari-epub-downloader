import uuid
from http.cookiejar import FileCookieJar, MozillaCookieJar
from pathlib import Path

from requests.cookies import RequestsCookieJar

from epubgen.EpubManager import EpubManager
from epubgen.SafariBook import SafariBook
from epubgen.SafariApi import SafariApi
from epubgen.ResourceDownloader import SafariBookResourceDownloader

import logging


class Identity:
    def __init__(self, cookie_file):
        jar = MozillaCookieJar(cookie_file)
        jar.load()
        # self.cookie = RequestsCookieJar(jar)
        self.cookie = jar
        self.id = f"uid_{uuid.uuid4()}"

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
