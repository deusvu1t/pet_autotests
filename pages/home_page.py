from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class HomePage(BasePage):
    PATH = "/"

    def __init__(self, page: Page):
        super().__init__(page)

    @property
    def search_input(self) -> Locator:
        return self.page.get_by_test_id("search-query")

    @property
    def search_submit(self) -> Locator:
        return self.page.get_by_test_id("search-submit")

    @property
    def product_cards(self) -> Locator:
        return self.page.locator('[data-test^="product-"]')

    def search(self, text: str):
        self.search_input.fill(text)
        self.search_submit.click()
