from playwright.sync_api import Locator


class ProductCard:
    def __init__(self, root: Locator) -> None:
        self.root: Locator = root

    @property
    def name(self) -> Locator:
        return self.root.locator("[data-test='product-name']")

    @property
    def price(self) -> Locator:
        return self.root.locator("[data-test='product-price']")

    @property
    def image(self) -> Locator:
        return self.root.locator("img")

    def open(self) -> None:
        self.root.click()
