from pathlib import Path

from EpubManager import EpubManager
from SafariBook import SafariBook;
from SafariApi import SafariApi
from SafariBookResourceDownloader import SafariBookResourceDownloader


class Main:
    def __init__(self, **kwargs):
        self.work_dir = kwargs.get("workdir", "work")
        self.username = kwargs["username"]
        self.password = kwargs["password"]
        self.api = SafariApi()
        self.downloader = SafariBookResourceDownloader(self.api)
        self.api.do_login(self.username, self.password)

    def retrieve_epub(self, book_id):
        working_path = "{}/{}".format(self.work_dir, book_id)
        path = Path(working_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        self.downloader.download(working_path, book_id)
        safari_book = SafariBook.from_json_file(working_path)
        EpubManager(safari_book).create_epub(self.work_dir)


