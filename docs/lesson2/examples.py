"""
Lesson 2 — Playwright locators.
All examples target https://practicesoftwaretesting.com/

Run from project root:
    pytest docs/lesson2/examples.py -v --headed
"""

import re

from playwright.sync_api import Page, expect


# ---------------------------------------------------------------------------
# 1. get_by_role — the most important one
# ---------------------------------------------------------------------------

def test_role_button(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # Sign in link in the header
    sign_in = page.get_by_role("link", name="Sign in")
    expect(sign_in).to_be_visible()
    sign_in.click()

    # Login form heading
    expect(page.get_by_role("heading", name="Login")).to_be_visible()


def test_role_with_regex_and_exact(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # Heading containing "Banner" — partial match via regex
    banner = page.get_by_role("heading", name=re.compile("Banner", re.IGNORECASE))
    expect(banner).to_be_visible()

    # Strict equality (no surrounding text allowed)
    home = page.get_by_role("link", name="Home", exact=True)
    expect(home).to_be_visible()


# ---------------------------------------------------------------------------
# 2. get_by_label — form fields
# ---------------------------------------------------------------------------

def test_label_login_form(page: Page):
    page.goto("https://practicesoftwaretesting.com/auth/login")

    # The login form has labels — we use them, not data-test
    page.get_by_label("Email address").fill("customer@practicesoftwaretesting.com")
    page.get_by_label("Password").fill("welcome01")

    page.get_by_role("button", name="Login").click()

    # If login succeeded, "My account" page heading shows up
    expect(page.get_by_role("heading", name="My account")).to_be_visible()


# ---------------------------------------------------------------------------
# 3. get_by_placeholder — when there is no proper label
# ---------------------------------------------------------------------------

def test_placeholder_search(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # The search input only has a placeholder, no label
    page.get_by_placeholder("Search").fill("hammer")
    page.get_by_test_id("search-submit").click()

    # Results appear on the same page, header changes
    expect(page.get_by_test_id("search-caption")).to_contain_text("hammer")


# ---------------------------------------------------------------------------
# 4. get_by_text — for non-interactive elements
# ---------------------------------------------------------------------------

def test_text_partial_and_exact(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # Partial match — finds any element containing "Banner"
    expect(page.get_by_text("Banner").first).to_be_visible()

    # Exact match — node must equal exactly
    expect(page.get_by_text("Categories", exact=True)).to_be_visible()


# ---------------------------------------------------------------------------
# 5. get_by_alt_text — images
# ---------------------------------------------------------------------------

def test_alt_text_logo(page: Page):
    page.goto("https://practicesoftwaretesting.com/")
    # Hover-to-find: open the page, hover the logo, you'll see its alt
    expect(page.get_by_alt_text(re.compile("Banner", re.IGNORECASE))).to_be_visible()


# ---------------------------------------------------------------------------
# 6. get_by_title — elements with title (tooltip)
# ---------------------------------------------------------------------------

def test_title_attribute(page: Page):
    page.goto("https://practicesoftwaretesting.com/")
    # Most elements on this site don't use title="...", so this is for demo only.
    # On a real site you'd see something like:
    # expect(page.get_by_title("Help")).to_be_visible()


# ---------------------------------------------------------------------------
# 7. get_by_test_id — last resort, but common on practicesoftwaretesting.com
# ---------------------------------------------------------------------------

def test_test_id_search(page: Page):
    # Note: project conftest sets test_id_attribute to "data-test"
    page.goto("https://practicesoftwaretesting.com/")

    page.get_by_test_id("search-query").fill("pliers")
    page.get_by_test_id("search-submit").click()

    # All matching product cards
    products = page.get_by_test_id("product-name")
    expect(products).not_to_have_count(0)


# ---------------------------------------------------------------------------
# Chaining — scoping a locator to a smaller area
# ---------------------------------------------------------------------------

def test_chaining_scope(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # Find "Sign in" only inside the navigation header — not on the page body
    header = page.get_by_role("navigation")
    header.get_by_role("link", name="Sign in").click()

    expect(page.get_by_role("heading", name="Login")).to_be_visible()


# ---------------------------------------------------------------------------
# .filter() — find a card BY its content
# ---------------------------------------------------------------------------

def test_filter_by_text(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # Each card has data-test="product-..." (e.g. product-01J...)
    # We pick the one containing the text "Pliers"
    product_card = page.locator("[data-test^='product-']").filter(has_text="Pliers").first
    expect(product_card).to_be_visible()
    product_card.click()

    # Now we're on the product detail page
    expect(page.get_by_test_id("product-name")).to_contain_text("Pliers")


def test_filter_has_locator(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # Cards that contain a price element with "$" inside
    cards_with_price = page.locator("[data-test^='product-']").filter(
        has=page.locator("[data-test='product-price']")
    )
    # Every card on this site has a price — count should match total products
    expect(cards_with_price.first).to_be_visible()


# ---------------------------------------------------------------------------
# .first / .last / .nth() — picking one of many
# ---------------------------------------------------------------------------

def test_first_last_nth(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    products = page.get_by_test_id("product-name")
    expect(products.first).to_be_visible()
    expect(products.last).to_be_visible()
    expect(products.nth(2)).to_be_visible()  # third product


# ---------------------------------------------------------------------------
# Strict mode demo — what happens when locator matches multiple
# ---------------------------------------------------------------------------

def test_strict_mode_violation_demo(page: Page):
    """
    This shows how strict mode protects you from accidentally clicking
    the wrong element. The next test fixes it.
    """
    page.goto("https://practicesoftwaretesting.com/")
    add_buttons = page.get_by_test_id("product-name")
    # add_buttons.click()  # would raise strict mode violation
    expect(add_buttons.first).to_be_visible()


def test_strict_mode_fixed_via_scope(page: Page):
    """
    Better fix: scope the locator instead of using .first blindly.
    """
    page.goto("https://practicesoftwaretesting.com/")
    # Pick the FIRST product card explicitly via filter, not blind .first
    pliers_card = page.locator("[data-test^='product-']").filter(has_text="Pliers").first
    pliers_card.click()
    expect(page.get_by_test_id("product-name")).to_contain_text("Pliers")


# ---------------------------------------------------------------------------
# Why expect() beats time.sleep — auto-wait demo
# ---------------------------------------------------------------------------

def test_no_sleep_needed(page: Page):
    """
    Search returns results asynchronously. We don't sleep — expect() waits
    for the products to be re-rendered automatically.
    """
    page.goto("https://practicesoftwaretesting.com/")

    page.get_by_test_id("search-query").fill("saw")
    page.get_by_test_id("search-submit").click()

    # No sleep, no wait_for_timeout — expect waits up to 5 seconds for the
    # search results to render. If they appear in 200ms, test continues immediately.
    expect(page.get_by_test_id("search-caption")).to_contain_text("saw")
