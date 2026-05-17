import re

import pytest
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage
from utils.test_data import VALID_LOGIN_USER


@pytest.mark.smoke
@pytest.mark.ui
def test_user_menu_opens_after_login(page: Page):
    login_page = LoginPage(page).open()
    login_page.login_successfully(VALID_LOGIN_USER["email"], VALID_LOGIN_USER["password"])

    login_page.header.user_menu.open()

    expect(login_page.header.user_menu.my_account_link).to_be_visible()
    expect(login_page.header.user_menu.sign_out_button).to_be_visible()


@pytest.mark.ui
def test_sign_out_via_user_menu(page: Page):
    login_page = LoginPage(page).open()
    login_page.login_successfully(VALID_LOGIN_USER["email"], VALID_LOGIN_USER["password"])

    login_page.header.user_menu.sign_out()

    expect(page).to_have_url(re.compile(".*auth/login"))


@pytest.mark.ui
def test_user_menu_hidden_before_login(page: Page):
    login_page = LoginPage(page).open()

    expect(login_page.header.user_menu.trigger).to_be_hidden()
