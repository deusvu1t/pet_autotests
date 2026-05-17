import re

import pytest
from playwright.sync_api import Page, expect

from pages.register_page import RegisterPage


@pytest.mark.ui
def test_country_dropdown_has_many_options(page: Page):
    register_page = RegisterPage(page).open()

    countries = register_page.country_options()

    assert len(countries) > 100


@pytest.mark.ui
def test_country_dropdown_has_specific_countries(page: Page):
    register_page = RegisterPage(page).open()

    expect(register_page.country_dropdown.locator("option")).to_contain_text(
        ["Canada", "Germany", "United States of America (the)"]
    )


@pytest.mark.ui
def test_country_dropdown_first_option_is_placeholder(page: Page):
    register_page = RegisterPage(page).open()

    expect(register_page.country_dropdown.locator("option").first).to_have_text(
        re.compile("Your country")
    )
