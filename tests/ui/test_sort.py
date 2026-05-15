import pytest
from playwright.sync_api import Page, expect

from pages.home_page import HomePage
from utils.parsers import parse_price


@pytest.mark.ui
def test_sort_by_price_ascending(page: Page):
    home_page = HomePage(page).open()

    home_page.sort_by("Price (Low - High)")

    first_card_price = home_page.card_at(0).get_price()
    second_card_price = home_page.card_at(1).get_price()

    assert parse_price(first_card_price) <= parse_price(second_card_price)


@pytest.mark.ui
def test_sort_dropdown_options_present(page: Page):
    home_page = HomePage(page).open()

    options = home_page.sort_dropdown.locator("option")

    expect(options).to_contain_text(
        [
            "Name (A - Z)",
            "Price (Low - High)",
        ]
    )
