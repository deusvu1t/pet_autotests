from playwright.sync_api import Locator

from pages.base_page import BasePage
from pages.components.product_card import ProductCard
from utils.parsers import parse_price


class HomePage(BasePage):
    PATH = "/"

    @property
    def search_input(self) -> Locator:
        return self.page.get_by_test_id("search-query")

    @property
    def search_submit(self) -> Locator:
        return self.page.get_by_test_id("search-submit")

    @property
    def product_cards(self) -> Locator:
        return self.page.locator("a[data-test^='product-']")

    @property
    def product_names_list(self) -> Locator:
        return self.page.locator("[data-test='product-name']")

    @property
    def product_prices(self) -> Locator:
        return self.page.locator("[data-test='product-price']")

    @property
    def sort_dropdown(self) -> Locator:
        return self.page.get_by_test_id("sort")

    def sort_options(self) -> list[str]:
        options = self.sort_dropdown.locator("option")
        options.first.wait_for(state="attached")
        return options.all_inner_texts()

    def get_prices(self) -> list[float]:
        return [parse_price(p) for p in self.product_prices.all_inner_texts()]

    def get_names(self) -> list[str]:
        return self.product_names_list.all_inner_texts()

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

    def get_card_by_price(self, price: str) -> ProductCard:
        self.product_cards.first.wait_for()
        return ProductCard(
            self.page.locator(
                f"//span[@data-test='product-price' and normalize-space(text())='{price}']"
                "/ancestor::a[starts-with(@data-test,'product-')]"
            ).first
        )

    def category_checkbox(self, name: str) -> Locator:
        return self.page.get_by_role("checkbox", name=name)

    def select_categories(self, names: list[str]) -> None:
        for name in names:
            self.category_checkbox(name).check()

    def clear_filters(self) -> None:
        checkboxes = self.page.get_by_role("checkbox").all()
        for checkbox in checkboxes:
            if checkbox.is_checked():
                checkbox.uncheck()

    def sort_by(self, option: str) -> None:
        self.sort_dropdown.select_option(label=option)
