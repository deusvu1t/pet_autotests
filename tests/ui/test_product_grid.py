import pytest
from playwright.sync_api import Page, expect

from pages.components.product_card import ProductCard
from pages.home_page import HomePage


@pytest.mark.ui
def test_first_product_card_has_full_layout(page: Page):
    home_page = HomePage(page).open()
    card = home_page.product_cards.filter(
        has=page.locator("[data-test='product-price']")
    ).first
    card_component = ProductCard(card)

    expect(card_component.name).to_be_visible()
    expect(card_component.price).to_be_visible()
    expect(card_component.image).to_be_visible()


@pytest.mark.ui
def test_grid_contains_at_least_n_products(page: Page):
    home_page = HomePage(page).open()

    expect(home_page.product_cards).not_to_have_count(0)
    expect(home_page.product_cards).to_have_count(9)


@pytest.mark.ui
def test_open_card_via_component(page: Page):
    home_page = HomePage(page).open()

    home_page.get_card_by_name("Hammer").open()

    expect(page.get_by_role("heading", level=1)).to_have_text("Hammer")


@pytest.mark.ui
def test_card_at_index(page: Page):
    home_page = HomePage(page).open()

    card = home_page.card_at(2)

    expect(card.name).to_be_visible()
