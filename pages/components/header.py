from playwright.sync_api import Locator, Page


class Header:
    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def logo(self) -> Locator:
        return self.page.get_by_title("Practice Software Testing - Toolshop")

    @property
    def sign_in(self) -> Locator:
        return self.page.get_by_test_id("nav-sign-in")

    @property
    def cart_icon(self) -> Locator:
        return self.page.locator('[data-icon="cart-shopping"]')

    @property
    def cart_quantity(self) -> Locator:
        return self.page.get_by_test_id("cart-quantity")
