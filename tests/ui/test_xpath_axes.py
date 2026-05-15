import pytest
from playwright.sync_api import Page, expect

from pages.home_page import HomePage


@pytest.mark.ui
def test_card_found_by_price_via_ancestor(page: Page):
    home = HomePage(page).open()
    card = home.get_card_by_price("$12.58")
    expect(card.name).to_be_visible()
