from epubgen.EpubManager import EpubManager
from epubgen.SafariApi import SafariApi
from epubgen.SafariBook import SafariBook


def test_get_base_name_of_url():
    base_name = SafariApi.get_basename_of_url("http://www.sina.com.cn/blabla/something/abc.html")
    assert base_name == "abc.html"


def test_generate_epub():
    safari_book = SafariBook.\
        from_json_file("work/9781449370831/info.json", "work/9781449370831/chapters.json", "work/9781449370831/toc.json")
    epub_manager = EpubManager(safari_book)
    epub_manager.create_epub("work")

