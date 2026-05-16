from playwright.sync_api import Locator

from pages.base_page import BasePage


class ContactPage(BasePage):
    PATH = "/contact"

    @property
    def first_name_input(self) -> Locator:
        return self.page.get_by_label("First name")

    @property
    def last_name_input(self) -> Locator:
        return self.page.get_by_label("Last name")

    @property
    def email_input(self) -> Locator:
        return self.page.get_by_label("Email address")

    @property
    def subject_dropdown(self) -> Locator:
        return self.page.get_by_label("Subject")

    @property
    def message_textarea(self) -> Locator:
        return self.page.get_by_label("Message")

    @property
    def attachment_input(self) -> Locator:
        return self.page.locator("input[type='file']")

    @property
    def send_button(self) -> Locator:
        return self.page.get_by_role("button", name="Send")

    @property
    def success_alert(self) -> Locator:
        return self.page.get_by_role("alert")

    def error_for(self, field: str) -> Locator:
        return self.page.get_by_test_id(f"{field}-error")

    def submit_contact_form(self, data: dict, attachment: str | None = None) -> None:
        self.first_name_input.fill(data["first_name"])
        self.last_name_input.fill(data["last_name"])
        self.email_input.fill(data["email"])
        self.subject_dropdown.select_option(label=data["subject"])
        self.message_textarea.fill(data["message"])

        if attachment:
            self.attachment_input.set_input_files(attachment)

        self.send_button.click()
