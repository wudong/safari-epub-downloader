from pathlib import Path

from SafariBook import SafariBook
from ebooklib import epub


class EpubManager:

    def __init__(self, book: SafariBook):
        self.book = book
        self.epub_book = EpubManager.init_epub_book(book)
        self.lang = book.get_language()
        self.book_id = book.get_book_id()

    @staticmethod
    def init_epub_book(safari_book: SafariBook):
        book = epub.EpubBook()
        book.set_title(safari_book.get_title())
        book.set_language(safari_book.get_language())
        book.set_identifier(safari_book.get_isbn())
        #book.spine.append('cover')
        #book.spine.append('nav')

        for author in safari_book.get_authors():
            book.add_author(author)

        return book

    def add_chapter(self, chapter):
        file_name = chapter["full_path"]
        title = chapter["title"]

        file_name_xhtml = file_name
        #str(Path(file_name).with_suffix(".xhtml"))

        item = epub.EpubHtml(title=title,
                             file_name=file_name_xhtml,
                             lang=self.book.get_language())

        for ss in [stylesheet["full_path"] for stylesheet in chapter["stylesheets"]]:
            item.add_link(href=ss, rel='stylesheet', type='text/css')

        item.content = self.book.get_text_content(file_name)
        self.epub_book.add_item(item)
        self.epub_book.spine.append(item)

    def add_image(self, image_filename):
        item = epub.EpubImage()
        item.id = "image_" + image_filename
        item.file_name = image_filename
        item.media_type = "image/jpeg"
        item.content = self.book.get_binary_content(image_filename)
        self.epub_book.add_item(item)

    def add_style(self, style_filename):
        item = epub.EpubItem(uid="style_" + style_filename,
                             file_name=style_filename,
                             media_type="text/css")
        item.content = self.book.get_text_content(style_filename)
        self.epub_book.add_item(item)

    def write_to_file(self, workdir):
        file_name = "{}/{}.epub".format(workdir, self.book.get_book_id())
        epub.write_epub(file_name, self.epub_book, {})

    def create_epub(self, workdir):
        self.epub_book.set_cover("cover.jpg", self.book.get_binary_content("cover.jpg"), False)

        for chapter in self.book.get_book_chapters():
            self.add_chapter(chapter)

        for image in self.book.get_images():
            self.add_image(image)

        for style in self.book.get_styles():
            self.add_style(style)

        self.epub_book.add_item(epub.EpubNcx())
        self.epub_book.add_item(epub.EpubNav())
        self.epub_book.toc = EpubManager.convert_toc(self.book.get_toc())

        self.write_to_file(workdir)

    @staticmethod
    def convert_toc(toc_json):
        return [EpubManager.toc_recursive(toc_element) for toc_element in toc_json]

    @staticmethod
    def toc_recursive(toc_element):
        children_elements = toc_element["children"]
        if children_elements and len(children_elements) > 0:
            return (EpubManager.toc_to_epubsection(toc_element),
                    [EpubManager.toc_recursive(child) for child in children_elements])
        else:
            return EpubManager.toc_to_epublink(toc_element)

    @staticmethod
    def toc_to_epublink(toc_element):
        return epub.Link(toc_element["href"], toc_element["label"], toc_element["id"])

    def toc_to_epubsection(toc_element):
        return epub.Section(toc_element["label"], toc_element["href"])