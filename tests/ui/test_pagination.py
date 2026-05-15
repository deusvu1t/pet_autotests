import pytest
from playwright.sync_api import Page

from pages.home_page import HomePage


@pytest.mark.ui
def test_go_to_next_page(page: Page):
    home_page = HomePage(page).open()

    home_page.pagination.go_to_next_page()

    assert home_page.pagination.current_page() == 2


@pytest.mark.ui
def test_go_to_second_page(page: Page):
    home_page = HomePage(page).open()

    home_page.pagination.go_to_page(2)

    assert home_page.pagination.current_page() == 2


@pytest.mark.ui
def test_go_to_last_page(page: Page):
    home_page = HomePage(page).open()

    home_page.pagination.go_to_last_page()

    assert home_page.pagination.current_page() > 1
