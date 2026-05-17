"""
Lesson 3 — CSS selectors in Playwright.
Target site: https://practicesoftwaretesting.com/

Run from project root:
    pytest docs/lesson3/examples.py -v --headed
"""

from playwright.sync_api import Page, expect


# ---------------------------------------------------------------------------
# 1. Basic selectors: tag, #id, .class, attribute
# ---------------------------------------------------------------------------

def test_basic_tag_class_attribute(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # Tag selector — every <img> on the page
    images = page.locator("img")
    expect(images.first).to_be_visible()

    # Class selector — generic Bootstrap container
    expect(page.locator(".container").first).to_be_visible()

    # Attribute selector — link to /auth/login
    sign_in = page.locator("a[href='/auth/login']")
    expect(sign_in).to_be_visible()


# ---------------------------------------------------------------------------
# 2. Attribute matching: ^=, *=, $=
# ---------------------------------------------------------------------------

def test_attribute_starts_with(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # Every product card has data-test="product-<id>"
    # ^= means "starts with"
    cards = page.locator("[data-test^='product-']")
    expect(cards.first).to_be_visible()


def test_attribute_contains(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # *= means "contains anywhere"
    # Most navigation links have "nav" somewhere in data-test
    nav_items = page.locator("[data-test*='nav-']")
    expect(nav_items.first).to_be_visible()


def test_attribute_ends_with(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # $= means "ends with"
    # Find images that point to .jpg files
    jpg_images = page.locator("img[src$='.jpg']")
    # The site might have 0 jpgs — this just demonstrates syntax
    # so we don't assert count, just check selector parses
    _ = jpg_images.count()


# ---------------------------------------------------------------------------
# 3. Combinators: descendant ( ), child (>), sibling (+)
# ---------------------------------------------------------------------------

def test_descendant_combinator(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # Any <a> inside the navigation, no matter how deep
    nav_links = page.locator("nav a")
    expect(nav_links.first).to_be_visible()


def test_direct_child_combinator(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # Direct children of the product grid container
    # (would not include nested elements)
    grid_items = page.locator("[data-test='product-name']")
    expect(grid_items.first).to_be_visible()


# ---------------------------------------------------------------------------
# 4. :nth-child vs :nth-of-type
# ---------------------------------------------------------------------------

def test_nth_child_demo(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # In Playwright the idiomatic way is .nth(N) — equivalent to :nth-child(N+1)
    products = page.locator("[data-test^='product-']")
    expect(products.nth(0)).to_be_visible()  # first
    expect(products.nth(2)).to_be_visible()  # third

    # Pure CSS equivalent — note: nth-child counts ALL siblings
    # On this site product cards are wrapped, so :nth-child may behave
    # differently than .nth(). When in doubt — use .nth().


# ---------------------------------------------------------------------------
# 5. :not() — exclusion
# ---------------------------------------------------------------------------

def test_not_pseudo_class(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # All links that are NOT external (no target="_blank")
    internal_links = page.locator("a:not([target='_blank'])")
    expect(internal_links.first).to_be_visible()


# ---------------------------------------------------------------------------
# 6. :has() — the modern XPath replacement
# ---------------------------------------------------------------------------

def test_has_pseudo_class(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # Cards that have a price element inside
    # Same idea as .filter(has=page.locator("[data-test='product-price']"))
    cards_with_price = page.locator("[data-test^='product-']:has([data-test='product-price'])")
    expect(cards_with_price.first).to_be_visible()


def test_has_text_pseudo(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # Card containing the text "Pliers" anywhere inside
    pliers_card = page.locator("[data-test^='product-']:has-text('Pliers')").first
    expect(pliers_card).to_be_visible()


# ---------------------------------------------------------------------------
# 7. Chaining via >> (Playwright shortcut)
# ---------------------------------------------------------------------------

def test_chaining_with_double_arrow(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # Same as page.locator("nav").locator("a")
    nav_link = page.locator("nav >> a").first
    expect(nav_link).to_be_visible()


# ---------------------------------------------------------------------------
# 8. :visible — only what user sees
# ---------------------------------------------------------------------------

def test_visible_pseudo(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # Only product cards that are currently rendered (not display:none)
    visible_cards = page.locator("[data-test^='product-']:visible")
    expect(visible_cards.first).to_be_visible()


# ---------------------------------------------------------------------------
# 9. Combining everything — real test
# ---------------------------------------------------------------------------

def test_realistic_combo(page: Page):
    """
    Find a product card by name using CSS only (no get_by_*).
    Demonstrates that CSS can do everything get_by_* can — but uglier.
    This is a teaching example, not a recommendation.
    """
    page.goto("https://practicesoftwaretesting.com/")

    # Card containing product-name with text "Pliers"
    card = page.locator("[data-test^='product-']:has(*:text-is('Pliers'))").first
    expect(card).to_be_visible()

    # Click the card and verify we landed on a product page
    card.click()
    expect(page.locator("[data-test='product-name']")).to_contain_text("Pliers")


# ---------------------------------------------------------------------------
# 10. Anti-pattern demo — what NOT to do
# ---------------------------------------------------------------------------

def test_antipattern_absolute_path():
    """
    DO NOT do this in real tests. Absolute paths break on any DOM change.
    """
    # page.locator("html > body > div > main > section > div > h2")
    pass


def test_antipattern_print_instead_of_expect(page: Page):
    """
    DO NOT use print() to validate — it doesn't fail tests, doesn't auto-wait,
    doesn't appear in reports.
    """
    page.goto("https://practicesoftwaretesting.com/")

    # ❌ Wrong way (commented out as the example of what not to do)
    # title = page.locator("[data-test='product-name']").first.text_content()
    # print("First product:", title)

    # ✅ Right way
    expect(page.locator("[data-test='product-name']").first).to_be_visible()


def test_antipattern_no_sleep_needed(page: Page):
    """
    Search results render asynchronously — no sleep needed,
    expect() auto-waits up to 5 seconds.
    """
    page.goto("https://practicesoftwaretesting.com/")

    page.locator("[data-test='search-query']").fill("hammer")
    page.locator("[data-test='search-submit']").click()

    # No wait_for_timeout, no sleep
    expect(page.locator("[data-test='search-caption']")).to_contain_text("hammer")
