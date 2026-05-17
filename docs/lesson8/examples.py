"""
Lesson 8 examples — working with tables in Playwright.

Working examples on:
  1) Classic <table> from testautomationpractice.blogspot.com (study site)
  2) Real cart table on practicesoftwaretesting.com

Run any test individually:
    pytest docs/lesson8/examples.py::test_static_table_basics -s
"""
import re

import pytest
from playwright.sync_api import Locator, Page, expect


# ---------------------------------------------------------------------------
# Part 1 — classic <table>
# ---------------------------------------------------------------------------

def test_static_table_basics(page: Page) -> None:
    """Find table, count rows/columns, read a specific row."""
    page.goto("https://testautomationpractice.blogspot.com/")

    table = page.locator("table[name='BookTable'] tbody")
    expect(table).to_be_visible()

    rows = table.locator("tr")
    expect(rows).to_have_count(7)               # 1 header + 6 data rows

    headers = rows.first.locator("th")
    expect(headers).to_have_count(4)            # Title / Author / Subject / Price

    second_row_cells = rows.nth(2).locator("td")
    expect(second_row_cells).to_have_text(
        ["Learn Java", "Mukesh", "Java", "500"]
    )


def test_read_table_as_list_of_dicts(page: Page) -> None:
    """Read whole table into a list[dict] for algorithmic checks."""
    page.goto("https://testautomationpractice.blogspot.com/")

    rows = page.locator("table[name='BookTable'] tbody tr")
    rows.first.wait_for()                       # required before .all()

    headers = ["title", "author", "subject", "price"]
    data: list[dict] = []
    # Skip [0] — that's the <th> header row
    for row in rows.all()[1:]:
        cells = row.locator("td").all_inner_texts()
        data.append(dict(zip(headers, cells)))

    # Now any algorithmic check is trivial
    mukesh_books = [b for b in data if b["author"] == "Mukesh"]
    assert len(mukesh_books) == 3

    total = sum(int(b["price"]) for b in data)
    assert total == 7100


def test_find_row_by_content(page: Page) -> None:
    """Find a row by content — the most common table operation."""
    page.goto("https://testautomationpractice.blogspot.com/")

    rows = page.locator("table[name='BookTable'] tbody tr")

    # Find the row containing "Cypress"
    cypress_row = rows.filter(has_text="Cypress")
    expect(cypress_row).to_be_visible()

    # Read cells from this row without knowing its index
    cells = cypress_row.locator("td").all_inner_texts()
    assert cells[0] == "Master In Cypress"
    assert cells[2] == "Cypress"


def test_filter_rows_by_column(page: Page) -> None:
    """Find rows where a specific column equals a value."""
    page.goto("https://testautomationpractice.blogspot.com/")

    rows = page.locator("table[name='BookTable'] tbody tr")

    # Rows where the 3rd cell (author) is exactly "Mukesh"
    # 'has' = nested locator that must match inside the row
    mukesh_rows = rows.filter(
        has=page.locator("td:nth-child(2)", has_text=re.compile(r"^Mukesh$"))
    )

    expect(mukesh_rows).to_have_count(3)


# ---------------------------------------------------------------------------
# Part 2 — real cart table on practicesoftwaretesting.com
# ---------------------------------------------------------------------------
#
# Flow:
#  1) Open product page
#  2) Add to cart
#  3) Navigate to /checkout
#  4) Inspect the cart table
#
# Note: the site renders the cart on /checkout as a real <table>.
# Open DevTools to confirm structure — data-test attributes are stable.

CART_BADGE = "[data-test='nav-cart']"


def _add_product_to_cart(page: Page, product_index: int = 0) -> None:
    """Helper — open a product and add it to the cart."""
    page.goto("https://practicesoftwaretesting.com/")
    page.locator("a[data-test^='product-']").first.wait_for()
    page.locator("a[data-test^='product-']").nth(product_index).click()
    page.locator("[data-test='add-to-cart-button']").click()
    # Wait for the cart counter to update — async API call
    expect(page.get_by_test_id("cart-quantity")).to_be_visible()


def test_cart_table_has_added_product(page: Page) -> None:
    """Add a product, open cart, verify the row exists."""
    _add_product_to_cart(page, 0)

    page.goto("https://practicesoftwaretesting.com/checkout")

    rows = page.locator("table tbody tr")
    expect(rows).to_have_count(1)


def test_cart_row_shows_product_data(page: Page) -> None:
    """Verify the cart row contains the right name, quantity, and prices."""
    _add_product_to_cart(page, 0)
    page.goto("https://practicesoftwaretesting.com/checkout")

    rows = page.locator("table tbody tr")
    rows.first.wait_for()

    row = rows.first
    name = row.locator("[data-test='product-title']").inner_text()
    qty = row.locator("[data-test='product-quantity']").input_value()

    assert name.strip() != ""
    assert qty == "1"


def test_total_equals_sum_of_subtotals(page: Page) -> None:
    """
    Cross-check: UI total must equal the sum of row subtotals.
    Catches arithmetic bugs in the cart summary.
    """
    _add_product_to_cart(page, 0)
    _add_product_to_cart(page, 1)

    page.goto("https://practicesoftwaretesting.com/checkout")

    rows = page.locator("table tbody tr")
    rows.first.wait_for()

    subtotals = [
        _parse_price(t)
        for t in rows.locator("[data-test='line-price']").all_inner_texts()
    ]
    total_ui = _parse_price(
        page.locator("[data-test='cart-total']").inner_text()
    )

    assert round(sum(subtotals), 2) == round(total_ui, 2)


def test_update_quantity_recalculates_subtotal(page: Page) -> None:
    """Change the quantity — subtotal must recalculate."""
    _add_product_to_cart(page, 0)
    page.goto("https://practicesoftwaretesting.com/checkout")

    rows = page.locator("table tbody tr")
    rows.first.wait_for()

    row = rows.first
    unit_price = _parse_price(
        row.locator("[data-test='product-price']").inner_text()
    )

    row.locator("[data-test='product-quantity']").fill("3")
    # Lose focus → SPA triggers recalculation
    row.locator("[data-test='product-quantity']").blur()

    expected_subtotal = round(unit_price * 3, 2)
    expect(row.locator("[data-test='line-price']")).to_have_text(
        re.compile(rf"\${expected_subtotal:.2f}")
    )


def test_remove_item_from_cart(page: Page) -> None:
    """Delete a row — verify it disappears from the table."""
    _add_product_to_cart(page, 0)
    page.goto("https://practicesoftwaretesting.com/checkout")

    rows = page.locator("table tbody tr")
    expect(rows).to_have_count(1)

    rows.first.locator("[data-test='product-remove']").click()

    expect(rows).to_have_count(0)


def test_empty_cart_state(page: Page) -> None:
    """An empty cart shows an empty-state message."""
    page.goto("https://practicesoftwaretesting.com/checkout")

    rows = page.locator("table tbody tr")
    expect(rows).to_have_count(0)
    expect(page.get_by_text(re.compile("empty", re.IGNORECASE))).to_be_visible()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_price(text: str) -> float:
    """Parse '$15.99' → 15.99."""
    return float(text.replace("$", "").strip())
