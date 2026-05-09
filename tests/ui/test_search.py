import pytest
from playwright.sync_api import Page, expect

from pages.home_page import HomePage


@pytest.mark.ui
def test_search_returns_matching_products(page: Page):
    home_page = HomePage(page).open()

    home_page.search("pliers")

    expect(home_page.product_cards.filter(has_text="Pliers")).not_to_have_count(0)


@pytest.mark.ui
def test_search_no_results(page):
    home_page = HomePage(page).open()

    home_page.search("123")

    expect(home_page.product_cards).to_have_count(0)
    expect(page.get_by_text("There are no products found.")).to_be_visible()


@pytest.mark.ui
def test_search_via_placeholder(page):
    HomePage(page).open()

    expect(page.get_by_placeholder("Search")).to_be_enabled()
