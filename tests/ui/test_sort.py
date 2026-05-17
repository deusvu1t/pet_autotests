import pytest
from playwright.sync_api import Page, expect

from pages.home_page import HomePage


@pytest.mark.ui
def test_sort_by_price_low_to_high(page: Page):
    home_page = HomePage(page).open()

    home_page.sort_by("Price (Low - High)")

    prices = home_page.get_prices()

    assert prices == sorted(prices)


@pytest.mark.ui
def test_sort_by_price_high_to_low(page: Page):
    home_page = HomePage(page).open()

    home_page.sort_by("Price (High - Low)")

    prices = home_page.get_prices()

    assert prices == sorted(prices, reverse=True)


@pytest.mark.ui
def test_sort_by_name_az_actually_sorts(page: Page):
    home_page = HomePage(page).open()

    home_page.sort_by("Name (A - Z)")

    names = home_page.get_names()

    assert names == sorted(names)


@pytest.mark.ui
def test_sort_by_name_za_actually_sorts(page: Page):
    home_page = HomePage(page).open()

    home_page.sort_by("Name (Z - A)")

    names = home_page.get_names()

    assert names == sorted(names, reverse=True)


@pytest.mark.ui
def test_sort_dropdown_options_present(page: Page):
    home_page = HomePage(page).open()

    expect(home_page.sort_dropdown.locator("option")).to_contain_text(
        [
            "",
            "Name (A - Z)",
            "Name (Z - A)",
            "Price (High - Low)",
            "Price (Low - High)",
            "CO₂ Rating (A - E)",
            "CO₂ Rating (E - A)",
        ]
    )
