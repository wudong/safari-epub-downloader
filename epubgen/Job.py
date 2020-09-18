import logging
import uuid
from enum import Enum

from epubgen.Facade import Facade
import os


work_dir = os.getenv("SAFARI_BOOK_DOWNLOADER_DIR", "work")


class Job:
    """
    Represent an converting job for a given book_id.
    """
    def __init__(self, book_id, identity, work_dir):
        self.book_id = book_id
        self.identity = identity
        self.status = Status.WAIT
        self.work_dir = work_dir
        self.id = f"job_{uuid.uuid4()}"

    def get_job_id(self):
        return self.id

    def execute(self):
        self.status = Status.STARTED
        logging.info(f"Starting job: {self}")

        # trying login
        try:
            main = Facade(identity=self.identity, work_dir=self.work_dir)
        except RuntimeError:
            self.status = Status.LOGIN_FAILED
            return

        self.status = Status.DOWNLOADING
        logging.info(f"Downloading for job: {self}")
        try:
            main.retrieve_epub(self.book_id)
        except RuntimeError:
            self.status = Status.DOWNLOADING_FAILED
            return

        logging.info(f"Generating for job: {self}")
        try:
            main.create_epub(self.book_id)
        except RuntimeError:
            self.status = Status.GENERATING_FAILED
            return

        logging.info(f"Job success: {self}")
        self.status = Status.SUCCESS

    def __str__(self):
        return f"Job{{book_id: {self.book_id}, identity: {self.identity.get_username()}, status: {self.status}}}"


class Status(Enum):
    WAIT = 0
    STARTED = 1
    DOWNLOADING = 2
    GENERATING = 3
    SUCCESS = 4
    DOWNLOADING_FAILED = 6
    GENERATING_FAILED = 7
    LOGIN_FAILED = 8

