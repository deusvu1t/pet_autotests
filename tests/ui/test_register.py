import re

import pytest
from playwright.sync_api import Page, expect

from pages.register_page import RegisterPage
from utils.test_data import valid_registration_data


@pytest.mark.smoke
@pytest.mark.ui
def test_register_page_opens(page: Page):
    register_page = RegisterPage(page).open()

    expect(register_page.first_name_input).to_be_visible()
    expect(register_page.last_name_input).to_be_visible()
    expect(register_page.date_of_birth_input).to_be_visible()
    expect(register_page.country_dropdown).to_be_visible()
    expect(register_page.postal_code_input).to_be_visible()
    expect(register_page.house_number_input).to_be_visible()
    expect(register_page.street_input).to_be_visible()
    expect(register_page.city_input).to_be_visible()
    expect(register_page.state_input).to_be_visible()
    expect(register_page.phone_input).to_be_visible()
    expect(register_page.email_input).to_be_visible()
    expect(register_page.password_input).to_be_visible()
    expect(register_page.register_button).to_be_visible()


@pytest.mark.ui
def test_register_field_types(page: Page):
    register_page = RegisterPage(page).open()

    expect(register_page.first_name_input).to_have_attribute("type", "text")
    expect(register_page.last_name_input).to_have_attribute("type", "text")
    expect(register_page.date_of_birth_input).to_have_attribute("type", "text")
    expect(register_page.postal_code_input).to_have_attribute("type", "text")
    expect(register_page.house_number_input).to_have_attribute("type", "text")
    expect(register_page.street_input).to_have_attribute("type", "text")
    expect(register_page.city_input).to_have_attribute("type", "text")
    expect(register_page.state_input).to_have_attribute("type", "text")
    expect(register_page.phone_input).to_have_attribute("type", "text")
    expect(register_page.email_input).to_have_attribute("type", "text")
    expect(register_page.password_input).to_have_attribute("type", "password")
    expect(register_page.register_button).to_have_attribute("type", "submit")


@pytest.mark.ui
def test_register_required_fields_validation(page: Page):
    register_page = RegisterPage(page).open()

    expect(register_page.first_name_input).to_have_attribute("aria-required", "true")
    expect(register_page.last_name_input).to_have_attribute("aria-required", "true")
    expect(register_page.date_of_birth_input).to_have_attribute("aria-required", "true")
    expect(register_page.postal_code_input).to_have_attribute("aria-required", "true")
    expect(register_page.house_number_input).to_have_attribute("aria-required", "true")
    expect(register_page.street_input).to_have_attribute("aria-required", "true")
    expect(register_page.city_input).to_have_attribute("aria-required", "true")
    expect(register_page.state_input).to_have_attribute("aria-required", "true")
    expect(register_page.phone_input).to_have_attribute("aria-required", "true")
    expect(register_page.email_input).to_have_attribute("aria-required", "true")


@pytest.mark.ui
def test_register_with_valid_data(page: Page):
    register_page = RegisterPage(page).open()

    data = valid_registration_data()

    register_page.register(data)

    expect(page).to_have_url(re.compile("/login"))


@pytest.mark.ui
def test_register_error_on_empty_submit(page: Page):
    register_page = RegisterPage(page).open()

    register_page.register_button.click()

    expect(register_page.error_for("first-name")).to_be_visible()
    expect(register_page.error_for("last-name")).to_be_visible()
    expect(register_page.error_for("dob")).to_be_visible()
    expect(register_page.error_for("country")).to_be_visible()
    expect(register_page.error_for("postal_code")).to_be_visible()
    expect(register_page.error_for("house_number")).to_be_visible()
    expect(register_page.error_for("street")).to_be_visible()
    expect(register_page.error_for("city")).to_be_visible()
    expect(register_page.error_for("state")).to_be_visible()
    expect(register_page.error_for("phone")).to_be_visible()
    expect(register_page.error_for("email")).to_be_visible()
    expect(register_page.error_for("password")).to_be_visible()
