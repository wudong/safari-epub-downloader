import json
from pathlib import Path

import SafariApi


class SafariBookResourceDownloader:

    def __init__(self, safari_api: SafariApi):
        self.api = safari_api

    def download(self, work_dir, book_id):
        info = self.api.get_book_info(book_id)
        chapters = self.api.get_all_book_chapters(book_id)
        self.download_all_resources(work_dir, book_id, info, chapters)

    def download_all_resources(self,
                               work_dir,
                               book_id,
                               book_info,
                               book_chapters):

        with open("{}/{}".format(work_dir, "info.json"), "w", encoding="utf8") as fh:
            json.dump(book_info, fh, indent=4, sort_keys=True)

        with open("{}/{}".format(work_dir, "chapters.json"), "w", encoding="utf8") as fh:
            json.dump(book_chapters, fh, indent=4, sort_keys=True)

        all_chapter_html_content_urls = [(chapter["content"], chapter['full_path'])
                                         for chapter in book_chapters]

        style_sheet_urls = [(stylesheet["url"], stylesheet['full_path'])
                            for chapter in book_chapters
                            for stylesheet in chapter["stylesheets"]]

        image_urls = [(chapter["asset_base_url"] + image, image)
                      for chapter in book_chapters
                      for image in chapter["images"]]

        cover_url = book_info["cover"]
        toc_url = book_info["toc"]

        self.api.download(work_dir, book_id, all_chapter_html_content_urls,
                          style_sheet_urls, image_urls, cover_url,
                          toc_url)
