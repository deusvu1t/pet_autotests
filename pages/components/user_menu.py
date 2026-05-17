from playwright.sync_api import Locator, Page, expect


class UserMenu:
    def __init__(self, page: Page):
        self.page = page

    @property
    def trigger(self) -> Locator:
        return self.page.get_by_test_id("nav-menu")

    @property
    def sign_out_button(self) -> Locator:
        return self.page.get_by_test_id("nav-sign-out")

    @property
    def my_account_link(self) -> Locator:
        return self.page.get_by_test_id("nav-my-account")

    def open(self) -> None:
        expect(self.trigger).to_be_visible(timeout=30_000)
        self.trigger.click()
        expect(self.sign_out_button).to_be_visible()

    def sign_out(self) -> None:
        self.open()
        self.sign_out_button.click()
