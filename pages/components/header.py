from playwright.sync_api import Page


class Header:
    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def logo(self):
        return self.page.get_by_title("Practice Software Testing - Toolshop")

    @property
    def sign_in(self):
        return self.page.get_by_test_id("nav-sign-in")

    @property
    def cart_icon(self):
        return self.page.locator('[data-icon="cart-shopping"]')

    @property
    def cart_quantity(self):
        return self.page.get_by_test_id("cart-quantity")
