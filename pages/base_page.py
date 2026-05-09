from urllib.parse import urljoin

from playwright.sync_api import Page

from utils.config import BASE_URL


class BasePage:
    PATH = ""

    def __init__(self, page: Page):
        self.page = page

    def open(self):
        self.page.goto(urljoin(BASE_URL, self.PATH))
        return self
