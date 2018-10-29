import os
import json
from pathlib import Path


class SafariBook:

    def __init__(self, **kwargs):
        self.book_info = kwargs["info"]
        self.chapters = kwargs["chapters"]
        self.toc = kwargs["toc"]
        self.book_id: str = self.book_info["natural_key"][0]
        self.folder: str = kwargs["folder"] if kwargs["folder"] else self.book_id

    def get_book_info(self):
        return self.book_info

    def get_book_chapters(self):
        return self.chapters

    def get_book_id(self):
        return self.book_id

    def get_toc(self):
        return self.toc

    def get_images(self):
        return set([image for chapter in self.chapters
                    for image in chapter["images"]])

    def get_styles(self):
        return set([stylesheet['full_path']
                    for chapter in self.chapters
                    for stylesheet in chapter["stylesheets"]])

    def get_text_content(self, filename):
        file_name = "{}/{}".format(self.folder, filename)
        return Path(file_name).read_text(encoding="utf-8")

    def get_language(self):
        return self.book_info["language"]

    def get_isbn(self):
        return self.book_info["isbn"]

    def get_title(self):
        return self.book_info["title"]

    def get_authors(self):
        return [author["name"] for author in self.book_info["authors"]]

    @staticmethod
    def from_json_file_from_work_dir(working_path):
        return SafariBook.from_json_file("{}/{}".format(working_path, "info.json"),
                                         "{}/{}".format(working_path, "chapters.json"),
                                         "{}/{}".format(working_path, "toc.json"),
                                         working_path)

    @staticmethod
    def from_json_file(info_file, chapter_file, toc_file, folder=None):
        def parse_json_file(file_name):
            with open(file_name) as fh:
                return json.load(fh)

        info_json = parse_json_file(info_file)
        chapters_json = parse_json_file(chapter_file)
        toc_json = parse_json_file(toc_file)

        return SafariBook(info=info_json,
                          chapters=chapters_json,
                          toc=toc_json,
                          folder=folder)

    def get_binary_content(self, filename):
        file_name = "{}/{}".format(self.folder, filename)
        return Path(file_name).read_bytes()
