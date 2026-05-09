import re

import pytest
from playwright.sync_api import Page, expect

from pages.home_page import HomePage
from utils.config import BASE_URL


@pytest.mark.smoke
@pytest.mark.ui
def test_home_opens(page: Page):
    HomePage(page).open()

    expect(page).to_have_url(f"{BASE_URL}/")
    expect(page).to_have_title(re.compile("Practice Software Testing"))


@pytest.mark.ui
def test_home_search_visible(page: Page):
    home = HomePage(page).open()

    expect(home.search_input).to_be_visible()
    expect(home.search_submit).to_be_visible()


@pytest.mark.ui
def test_home_products_loaded(page: Page):
    home = HomePage(page).open()

    expect(home.product_cards).not_to_have_count(0)
