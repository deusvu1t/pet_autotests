import pytest
from playwright.sync_api import Page, expect

from pages.contact_page import ContactPage
from utils.test_data import valid_contact_data


@pytest.mark.ui
def test_contact_form_submit(page: Page):
    contact_page = ContactPage(page).open()

    data = valid_contact_data()

    contact_page.submit_contact_form(data)

    expect(contact_page.success_alert).to_be_visible()


@pytest.mark.ui
def test_contact_attachment_upload(page: Page):
    contact_page = ContactPage(page).open()

    contact_page.attachment_input.set_input_files("utils/test_file.txt")

    expect(contact_page.attachment_input).not_to_be_empty()


@pytest.mark.ui
def test_contact_validation_message_required(page: Page):
    contact_page = ContactPage(page).open()

    contact_page.send_button.click()

    expect(contact_page.error_for("first-name")).to_be_visible()
    expect(contact_page.error_for("last-name")).to_be_visible()
    expect(contact_page.error_for("email")).to_be_visible()
    expect(contact_page.error_for("message")).to_be_visible()
