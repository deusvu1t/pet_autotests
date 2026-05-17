from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class LoginPage(BasePage):
    PATH = "/auth/login"

    def __init__(self, page: Page):
        super().__init__(page)

    @property
    def email_input(self) -> Locator:
        return self.page.get_by_label("Email address *")

    @property
    def password_input(self) -> Locator:
        return self.page.get_by_label("Password *")

    @property
    def login_button(self) -> Locator:
        return self.page.get_by_test_id("login-submit")

    def login(self, email: str, password: str) -> None:
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.login_button.click()
