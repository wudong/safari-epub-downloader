#!/usr/bin/env python3
# coding: utf-8
import os
import sys
import requests
import logging
from lxml import html, etree
from urllib.parse import urljoin, urlsplit, urlparse
from pathlib import Path

PATH = os.path.dirname(os.path.realpath(__file__))
COOKIES_FILE = os.path.join(PATH, "cookies.json")


class SafariApi:
    BASE_URL = "https://www.safaribooksonline.com"
    LOGIN_URL = BASE_URL + "/accounts/login/"
    API_TEMPLATE = BASE_URL + "/api/v1/book/{0}/"

    HEADERS = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-encoding": "gzip, deflate",
        "accept-language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "cookie": "",
        "pragma": "no-cache",
        "referer": "https://www.safaribooksonline.com/home/",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/62.0.3202.94 Safari/537.36"
    }

    def __init__(self):
        # a dictionary represent the cookies.
        self.cookies = {}

    @staticmethod
    def request_error_logging_and_exit(*error_message):
        logging.error("Error while making request: ", "\n".join(error_message))
        sys.exit(1)

    @staticmethod
    def write_response_to_file(response, filename):
        # making sure the path's parent exists.
        if not Path(filename).parent.exists():
            Path(filename).parent.mkdir(parents=True, exist_ok=True)

        with open(filename, 'wb') as i:
            for chunk in response.iter_content(1024):
                i.write(chunk)

    def get_api_url(self, book_id: str):
        return self.API_TEMPLATE.format(book_id)

    def requests_provider(self, url, post=False, data=None, update_cookies=True, **kwargs):
        try:
            response = getattr(requests, "post" if post else "get")(
                url,
                headers=self.return_headers(url),
                data=data,
                **kwargs
            )

            last_request = (
                url, data, kwargs, response.status_code, "\n".join(
                    ["\t{}: {}".format(*h) for h in response.headers.items()]
                ), response.text
            )
            logging.debug(last_request)

        except (requests.ConnectionError, requests.ConnectTimeout, requests.RequestException) as request_exception:
            logging.error(str(request_exception))
            return 0

        if update_cookies:
            self.update_cookies(response.cookies)

        return response

    def return_cookies(self):
        return " ".join(["{0}={1};".format(k, v) for k, v in self.cookies.items()])

    def return_headers(self, url):
        if "safaribooksonline" in urlsplit(url).netloc:
            self.HEADERS["cookie"] = self.return_cookies()

        else:
            self.HEADERS["cookie"] = ""

        return self.HEADERS

    def update_cookies(self, jar):
        for cookie in jar:
            self.cookies.update({
                cookie.name: cookie.value
            })

    def do_login(self, email, password):
        response = self.requests_provider(self.BASE_URL)
        if response == 0:
            logging.error("Login: unable to reach Safari Books Online. Try again...")

        csrf = []
        try:
            csrf = html.fromstring(response.text).xpath("//input[@name='csrfmiddlewaretoken'][@value]")

        except (html.etree.ParseError, html.etree.ParserError) as parsing_error:
            logging.error(parsing_error)
            SafariApi.request_error_logging_and_exit("Login: error trying to parse the home of Safari Books Online.")

        if not len(csrf):
            SafariApi.request_error_logging_and_exit("Login: no CSRF Token found in the page.",
                                                     "Unable to continue the login.",
                                                     "Try again...")

        csrf = csrf[0].attrib["value"]
        response = self.requests_provider(
            self.LOGIN_URL,
            post=True,
            data=(
                ("csrfmiddlewaretoken", ""), ("csrfmiddlewaretoken", csrf),
                ("email", email), ("password1", password),
                ("is_login_form", "true"), ("leaveblank", ""),
                ("dontchange", "http://")
            ),
            allow_redirects=False
        )

        if response == 0:
            SafariApi.request_error_logging_and_exit("Login: unable to perform auth to Safari Books Online.\n "
                                                     "Try again...")

        # redirect means success?
        if response.status_code != 302:
            try:
                error_page = html.fromstring(response.text)
                errors_message = error_page.xpath("//ul[@class='errorlist']//li/text()")
                recaptcha = error_page.xpath("//div[@class='g-recaptcha']")
                messages = (["    `%s`" % error for error in errors_message
                             if "password" in error or "email" in error] if len(errors_message) else []) + \
                           (["    `ReCaptcha required (wait or do logout from the website).`"] if len(
                               recaptcha) else [])
                logging.error(messages)
                SafariApi.request_error_logging_and_exit("Login: unable to perform auth login to Safari Books Online.")

            except (html.etree.ParseError, html.etree.ParserError) as parsing_error:
                logging.error(parsing_error)
                SafariApi.request_error_logging_and_exit(
                    "Login: your login went wrong and it encountered in an error" +
                    " trying to parse the login details of Safari Books Online. Try again..."
                )
        else:
            logging.info("Logging success")

    @staticmethod
    def response_to_json(response):
        if response == 0:
            SafariApi.request_error_logging_and_exit("API: unable to retrieve book info.")

        json_response = response.json()
        if not isinstance(json_response, dict) or len(json_response.keys()) == 1:
            SafariApi.request_error_logging_and_exit("Error while calling Book API", json_response)

        return json_response

    def get_toc(self, book_info):
        toc_url = book_info["toc"]
        response = self.requests_provider(toc_url)
        return SafariApi.response_to_json(response)

    def get_book_info(self, book_id):
        """
        Request the Json object for book info from the Book API.
        :param book_id: the book's id to request.
        :return: the json of the book info
        """
        book_api_url = self.get_api_url(book_id)
        response = self.requests_provider(book_api_url)
        json_response = SafariApi.response_to_json(response)

        if "last_chapter_read" in json_response:
            del json_response["last_chapter_read"]

        return json_response

    def get_book_chapters_page(self, book_id, page):
        """
        Get the book_id's chapters which is a paged request.
        :param book_id: the bookid
        :param page: the chapter index
        :return: the json object that represent the chapter.
        """
        book_api_url = self.get_api_url(book_id)
        response = self.requests_provider(urljoin(book_api_url, "chapter/?page=%s" % page))

        json_response = SafariApi.response_to_json(response)

        if "results" not in json_response or not len(json_response["results"]):
            SafariApi.request_error_logging_and_exit("API: unable to retrieve book chapters.")

        return json_response

    def get_all_book_chapters(self, book_id):
        result = []
        has_next_page = True
        page_index = 1

        while has_next_page:
            chapter_page_json = self.get_book_chapters_page(book_id, page_index)
            has_next_page = chapter_page_json["next"] is not None
            page_index += 1
            result += (chapter_page_json["results"])

        return result

    def get_and_write_cover_image_to_path(self, book_info, image_path):
        """
        Get the cover from the provided book_info object.
        :param image_path: the image path that the image that is going to be saved.
        :param book_info:
        :return: the filename where the image is stored.
        """
        response = self.requests_provider(book_info["cover"], update_cookies=False, stream=True)
        if response == 0:
            logging.error("Error trying to retrieve the cover: %s" % book_info["cover"])
            return False

        file_ext = response.headers["Content-Type"].split("/")[-1]
        # so this written the cover image into a file into the image directory.
        filename = os.path.join(image_path, "default_cover." + file_ext)
        self.write_response_to_file(response, filename)
        return filename

    def get_toc(self, book_id):
        response = self.requests_provider(urljoin(self.get_api_url(book_id), "toc/"))
        json_response = SafariApi.response_to_json(response)
        return json_response

    def get_and_parse_html(self, url):
        response = self.requests_provider(url)
        if response == 0 or response.status_code != 200:
            SafariApi.request_error_logging_and_exit(
                "Crawler: error trying to retrieve this page: ", url)

        root = None

        try:
            root = html.fromstring(response.text, base_url=self.BASE_URL)
        except (html.etree.ParseError, html.etree.ParserError) as parsing_error:
            logging.error(parsing_error)
            SafariApi.request_error_logging_and_exit(
                "Crawler: error trying to parse this page: ", url)

        return root

    def get_and_save_to_file(self, url, filename):
        """
        Get the content of url and write to the given filename.
        :param book_chapter:
        :param filename:
        :return:
        """
        response = self.requests_provider(url)
        SafariApi.write_response_to_file(response, filename)

    @staticmethod
    def get_basename_of_url(url):
        url_path = urlparse(url).path
        return url_path.split("/")[-1]

    def download(self, workdir, book_id, chapters_urls, stylesheet_urls,
                 images_urls, cover_url, toc_url):
        for resource in set(chapters_urls).union(stylesheet_urls).union(images_urls):
            base_name = resource[1]
            file_name = "{}/{}".format(workdir, base_name)
            self.get_and_save_to_file(resource[0], file_name)

        self.get_and_save_to_file(cover_url, "{}/cover.jpg".format(workdir))
        self.get_and_save_to_file(toc_url, "{}/toc.json".format(workdir))

