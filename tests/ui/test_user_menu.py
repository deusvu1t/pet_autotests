import re

import pytest
from playwright.sync_api import Page, expect

from pages.home_page import HomePage
from pages.login_page import LoginPage
from utils.config import BASE_URL
from utils.test_data import VALID_LOGIN_USER


@pytest.mark.smoke
@pytest.mark.ui
def test_user_menu_opens_after_login(page: Page):
    LoginPage(page).open().login_successfully(VALID_LOGIN_USER["email"], VALID_LOGIN_USER["password"])
    page.goto(BASE_URL)
    header = HomePage(page).header

    header.user_menu.open()

    expect(header.user_menu.my_account_link).to_be_visible()
    expect(header.user_menu.sign_out_button).to_be_visible()


@pytest.mark.ui
def test_sign_out_via_user_menu(page: Page):
    LoginPage(page).open().login_successfully(VALID_LOGIN_USER["email"], VALID_LOGIN_USER["password"])
    page.goto(BASE_URL)

    HomePage(page).header.user_menu.sign_out()

    expect(page).to_have_url(re.compile(".*auth/login"))


@pytest.mark.ui
def test_user_menu_hidden_before_login(page: Page):
    login_page = LoginPage(page).open()

    expect(login_page.header.user_menu.trigger).to_be_hidden()
