import pytest
from playwright.sync_api import Page, expect

from pages.home_page import HomePage
from pages.product_page import ProductPage


@pytest.mark.smoke
@pytest.mark.ui
def test_product_page_layout(page: Page):
    HomePage(page).open().card_at(0).open()
    product_page = ProductPage(page)

    expect(product_page.name).to_be_visible()
    expect(product_page.price).to_be_visible()
    expect(product_page.description).to_be_visible()
    expect(product_page.quantity_input).to_be_visible()
    expect(product_page.add_to_cart_button).to_be_visible()


@pytest.mark.ui
def test_increase_quantity(page: Page):
    HomePage(page).open().card_at(0).open()
    product_page = ProductPage(page)

    expect(product_page.quantity_input).to_be_editable()

    product_page.quantity_input.fill("2")

    expect(product_page.quantity_input).to_have_value("2")
