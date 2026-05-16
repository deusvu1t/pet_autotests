import re

import pytest
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage
from utils.test_data import INVALID_LOGIN_USER, VALID_LOGIN_USER


@pytest.mark.smoke
@pytest.mark.ui
def test_login_with_valid_credentials(page: Page):
    login_page = LoginPage(page).open()

    login_page.login(VALID_LOGIN_USER["email"], VALID_LOGIN_USER["password"])

    expect(page).to_have_url(re.compile("/account"))


@pytest.mark.ui
def test_login_with_invalid_credentials(page: Page):
    login_page = LoginPage(page).open()

    login_page.login(INVALID_LOGIN_USER["email"], INVALID_LOGIN_USER["password"])

    expect(page.get_by_text("Invalid email or password")).to_be_visible()


@pytest.mark.ui
def test_form_uses_labels(page: Page):
    LoginPage(page).open()

    expect(page.get_by_label("Email address *")).to_be_visible()
    expect(page.get_by_label("Password *")).to_be_visible()
