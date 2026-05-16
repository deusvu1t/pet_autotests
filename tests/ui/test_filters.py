import pytest
from playwright.sync_api import Page, expect

from pages.home_page import HomePage


@pytest.mark.ui
def test_select_multiple_categories(page: Page):
    home_page = HomePage(page).open()

    categories = ["Hand Tools", "Power Tools"]

    home_page.select_categories(categories)

    expect(home_page.category_checkbox(categories[0])).to_be_checked()
    expect(home_page.category_checkbox(categories[1])).to_be_checked()


@pytest.mark.ui
def test_clear_filters(page: Page):
    home_page = HomePage(page).open()

    categories = ["Hand Tools", "Power Tools"]

    home_page.select_categories(categories)

    home_page.clear_filters()

    expect(home_page.category_checkbox(categories[0])).not_to_be_checked()
    expect(home_page.category_checkbox(categories[1])).not_to_be_checked()
