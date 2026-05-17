from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage


class ProductPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    @property
    def name(self) -> Locator:
        return self.page.locator("[data-test='product-name']")

    @property
    def price(self) -> Locator:
        return self.page.locator("[data-test='unit-price']")

    @property
    def description(self) -> Locator:
        return self.page.locator("[data-test='product-description']")

    @property
    def quantity_input(self) -> Locator:
        return self.page.locator("[data-test='quantity']")

    @property
    def add_to_cart_button(self) -> Locator:
        return self.page.locator("[data-test='add-to-cart']")

    def add_to_cart(self, quantity: int = 1) -> None:
        self.quantity_input.fill(str(quantity))
        self.add_to_cart_button.click()
        expect(self.header.cart_quantity).to_be_visible()
