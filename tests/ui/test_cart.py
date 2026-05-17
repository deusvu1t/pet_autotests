import pytest
from playwright.sync_api import Page, expect

from pages.home_page import HomePage
from pages.product_page import ProductPage


@pytest.mark.ui
def test_cart_not_to_be_visible_at_zero(page: Page):
    home_page = HomePage(page).open()

    expect(home_page.header.cart_quantity).not_to_be_visible()


@pytest.mark.ui
def test_cart_counter_starts_at_one(page: Page):
    home_page = HomePage(page).open()
    product_page = ProductPage(page)

    home_page.card_at(0).open()

    product_page.add_to_cart()

    assert product_page.header.cart_count() == 1


@pytest.mark.ui
def test_cart_counter_label_visible(page: Page):
    home_page = HomePage(page).open()
    product_page = ProductPage(page)

    home_page.card_at(0).open()

    product_page.add_to_cart()

    expect(product_page.header.cart_quantity).to_have_text("1")
