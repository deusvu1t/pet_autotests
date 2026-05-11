from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from pages.components.product_card import ProductCard


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
        return self.page.locator("a[data-test^='product-']")

    def search(self, text: str) -> None:
        self.search_input.fill(text)
        self.search_submit.click()

    def cards(self) -> list[ProductCard]:
        self.product_cards.first.wait_for()
        return [ProductCard(card) for card in self.product_cards.all()]

    def card_at(self, index: int) -> ProductCard:
        self.product_cards.first.wait_for()
        return ProductCard(self.product_cards.nth(index))

    def get_card_by_name(self, name: str) -> ProductCard:
        self.product_cards.first.wait_for()
        return ProductCard(
            self.product_cards.filter(
                has=self.page.get_by_test_id("product-name").get_by_text(
                    name,
                    exact=True,
                )
            )
        )

    def category_checkbox(self, name: str) -> Locator:
        return self.page.get_by_role("checkbox", name=name)

    def filter_by_category(self, name: str) -> None:
        self.category_checkbox(name).check()
