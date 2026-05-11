import re

import pytest
from playwright.sync_api import Page, expect

from pages.home_page import HomePage
from pages.product_page import ProductPage


@pytest.mark.ui
def test_filter_by_hand_tools(page: Page):
    home_page = HomePage(page).open()

    home_page.filter_by_category("hand tools")

    expect(home_page.category_checkbox("hand tools")).to_be_checked()


@pytest.mark.ui
def test_open_product_card(page: Page):
    HomePage(page).open().get_card_by_name("Pliers").open()

    product_page = ProductPage(page)

    expect(page).to_have_url(re.compile("product/"))

    expect(product_page.name).to_have_text("Pliers")
