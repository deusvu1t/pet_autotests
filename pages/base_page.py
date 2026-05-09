from playwright.sync_api import Page

from pages.components.header import Header
from utils.config import BASE_URL


class BasePage:
    PATH = ""

    def __init__(self, page: Page):
        self.page = page
        self.header = Header(page)

    def open(self):
        if not BASE_URL:
            raise ValueError("BASE_URL is not set")

        url = f"{BASE_URL.rstrip('/')}{self.PATH}"

        self.page.goto(url)

        return self
