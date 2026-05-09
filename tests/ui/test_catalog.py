import pytest
from playwright.sync_api import Page, expect

from pages.home_page import HomePage


@pytest.mark.ui
def test_filter_by_hand_tools(page: Page):
    home_page = HomePage(page).open()

    home_page.filter_by_category("hand tools")

    expect(home_page.category_checkbox("hand tools")).to_be_checked()


@pytest.mark.ui
def test_open_product_card(page: Page):
    home_page = HomePage(page).open()

    home_page.open_product("Hammer")

    expect(page.get_by_role("heading", level=1)).to_have_text("Hammer")
