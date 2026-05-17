from playwright.sync_api import Locator

from pages.base_page import BasePage


class RegisterPage(BasePage):
    PATH = "/auth/register"

    @property
    def first_name_input(self) -> Locator:
        return self.page.get_by_label("First name")

    @property
    def last_name_input(self) -> Locator:
        return self.page.get_by_label("Last name")

    @property
    def date_of_birth_input(self) -> Locator:
        return self.page.get_by_label("Date of Birth *")

    @property
    def country_dropdown(self) -> Locator:
        return self.page.get_by_label("Country")

    @property
    def postal_code_input(self) -> Locator:
        return self.page.get_by_label("Postal code")

    @property
    def house_number_input(self) -> Locator:
        return self.page.get_by_label("House number")

    @property
    def street_input(self) -> Locator:
        return self.page.get_by_label("Street")

    @property
    def city_input(self) -> Locator:
        return self.page.get_by_label("City")

    @property
    def state_input(self) -> Locator:
        return self.page.get_by_label("State")

    @property
    def phone_input(self) -> Locator:
        return self.page.get_by_label("Phone")

    @property
    def email_input(self) -> Locator:
        return self.page.get_by_label("Email address")

    @property
    def password_input(self) -> Locator:
        return self.page.get_by_label("Password")

    @property
    def register_button(self) -> Locator:
        return self.page.get_by_role("button", name="Register ")

    def error_for(self, field: str) -> Locator:
        return self.page.get_by_test_id(f"{field}-error")

    def country_options(self) -> list[str]:
        options = self.country_dropdown.locator("option")
        options.nth(1).wait_for(state="attached")
        return [o.strip() for o in options.all_text_contents()]

    def register(self, data: dict) -> None:
        self.first_name_input.fill(data["first_name"])
        self.last_name_input.fill(data["last_name"])
        self.date_of_birth_input.fill(data["date_of_birth"])
        self.country_dropdown.select_option(label=data["country"])
        self.postal_code_input.fill(data["postal_code"])
        self.house_number_input.fill(data["house_number"])
        self.street_input.fill(data["street"])
        self.city_input.fill(data["city"])
        self.state_input.fill(data["state"])
        self.phone_input.fill(data["phone"])
        self.email_input.fill(data["email"])
        self.password_input.fill(data["password"])
        self.register_button.click()
