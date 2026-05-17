"""
Lesson 4 — XPath in Playwright.
Target site: https://practicesoftwaretesting.com/

Run from project root:
    pytest docs/lesson4/examples.py -v --headed

Remember the priority order:
    get_by_role > get_by_label > get_by_placeholder > get_by_text
        > get_by_test_id > locator("css") > locator("xpath")

XPath is the fallback to the fallback. These examples show *how* it works,
not where it's the best tool — usually it isn't.
"""

from playwright.sync_api import Page, expect


# ---------------------------------------------------------------------------
# 1. Relative XPath with a single attribute
# ---------------------------------------------------------------------------

def test_relative_xpath_with_attribute(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # //tag[@attribute='value']
    search = page.locator("//input[@data-test='search-query']")
    expect(search).to_be_visible()


# ---------------------------------------------------------------------------
# 2. contains() — partial attribute match
# ---------------------------------------------------------------------------

def test_contains_for_attribute(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # data-test contains 'product-' anywhere
    # Equivalent CSS: [data-test*='product-']
    cards = page.locator("//*[contains(@data-test, 'product-')]")
    expect(cards.first).to_be_visible()


# ---------------------------------------------------------------------------
# 3. starts-with() — attribute prefix
# ---------------------------------------------------------------------------

def test_starts_with_for_attribute(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # data-test starts with 'product-'
    # Equivalent CSS: [data-test^='product-']
    cards = page.locator("//a[starts-with(@data-test, 'product-')]")
    expect(cards.first).to_be_visible()


# ---------------------------------------------------------------------------
# 4. text() — exact text match
# ---------------------------------------------------------------------------

def test_text_exact_match(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # Sign-in link in the header — exact direct text
    sign_in = page.locator("//a[text()='Sign in']")
    expect(sign_in).to_be_visible()

    # Playwright API equivalent (preferred in real tests):
    expect(page.get_by_role("link", name="Sign in")).to_be_visible()


# ---------------------------------------------------------------------------
# 5. contains(text(), ...) — partial text match
# ---------------------------------------------------------------------------

def test_contains_in_text(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # Any element whose direct text contains 'Sign'
    matches = page.locator("//*[contains(text(), 'Sign')]")
    expect(matches.first).to_be_visible()


# ---------------------------------------------------------------------------
# 6. normalize-space() — text with surrounding whitespace
# ---------------------------------------------------------------------------

def test_normalize_space(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # If the visible text has extra spaces or newlines around it,
    # text()='Sign in' may not match. normalize-space() handles that.
    sign_in = page.locator("//a[normalize-space(text())='Sign in']")
    expect(sign_in).to_be_visible()


# ---------------------------------------------------------------------------
# 7. and / or — multiple conditions
# ---------------------------------------------------------------------------

def test_and_operator(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # An <input> that has BOTH the test id AND a placeholder
    search = page.locator(
        "//input[@data-test='search-query' and @placeholder='Search']"
    )
    expect(search).to_be_visible()


def test_or_operator(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # Either sign-in link OR the search input — at least one is on the page
    elements = page.locator(
        "//*[@data-test='nav-sign-in' or @data-test='search-query']"
    )
    expect(elements.first).to_be_visible()


# ---------------------------------------------------------------------------
# 8. position() and last()
# ---------------------------------------------------------------------------

def test_position_and_last(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # Wait for grid to render
    page.locator("//a[starts-with(@data-test, 'product-')]").first.wait_for()

    # First product card via [1]
    first_card = page.locator("//a[starts-with(@data-test, 'product-')][1]")
    expect(first_card).to_be_visible()

    # Note: //a[1] vs (//a)[1] are NOT the same.
    # //a[1] = each <a> that is the FIRST among its siblings (can be many).
    # (//a)[1] = THE first <a> in the whole document (always one).
    very_first_a = page.locator("(//a)[1]")
    expect(very_first_a).to_be_visible()


# ---------------------------------------------------------------------------
# 9. ancestor:: — navigate UP the DOM (the killer XPath feature)
# ---------------------------------------------------------------------------

def test_ancestor_axis(page: Page):
    """
    Find the product card that contains a specific product name.
    'Find this child, then walk up to the card container.'
    Pure CSS cannot do this — :has() goes down, not up.
    """
    page.goto("https://practicesoftwaretesting.com/")

    card = page.locator(
        "//span[@data-test='product-name' and normalize-space(text())='Combination Pliers']"
        "/ancestor::a[starts-with(@data-test, 'product-')]"
    )
    expect(card).to_be_visible()


# ---------------------------------------------------------------------------
# 10. parent:: / .. — direct parent
# ---------------------------------------------------------------------------

def test_parent_axis(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # Parent of the search input — usually a wrapping div/form
    parent = page.locator("//input[@data-test='search-query']/..")
    expect(parent).to_be_visible()


# ---------------------------------------------------------------------------
# 11. following-sibling:: — sibling after
# ---------------------------------------------------------------------------

def test_following_sibling(page: Page):
    """
    In a product card, find the price that follows the name.
    """
    page.goto("https://practicesoftwaretesting.com/")

    # Walk: name → its following-sibling that has data-test='product-price'
    price = page.locator(
        "//span[@data-test='product-name']"
        "/following-sibling::span[@data-test='product-price']"
    ).first
    expect(price).to_be_visible()


# ---------------------------------------------------------------------------
# 12. preceding-sibling:: — sibling before  (CSS cannot do this)
# ---------------------------------------------------------------------------

def test_preceding_sibling(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # From a price, walk back to the name that precedes it
    name = page.locator(
        "//span[@data-test='product-price']"
        "/preceding-sibling::span[@data-test='product-name']"
    ).first
    expect(name).to_be_visible()


# ---------------------------------------------------------------------------
# 13. not() — exclude
# ---------------------------------------------------------------------------

def test_not_function(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # All <a> that are NOT external (no target='_blank')
    internal = page.locator("//a[not(@target='_blank')]")
    expect(internal.first).to_be_visible()


# ---------------------------------------------------------------------------
# 14. Wildcard * — any tag with a given attribute
# ---------------------------------------------------------------------------

def test_wildcard(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # Any element with this data-test, regardless of tag
    any_tag = page.locator("//*[@data-test='search-query']")
    expect(any_tag).to_be_visible()


# ---------------------------------------------------------------------------
# 15. Three ways to do the same thing — compare and choose
# ---------------------------------------------------------------------------

def test_three_ways_to_find_a_product_by_name(page: Page):
    """
    Goal: find the product card whose name is 'Pliers'.
    Same result, three implementations — pick the most readable in real tests.
    """
    page.goto("https://practicesoftwaretesting.com/")

    # 1) Playwright API — clearest, recommended
    by_api = (
        page.locator("[data-test^='product-']")
        .filter(has=page.get_by_test_id("product-name").get_by_text("Pliers", exact=True))
    ).first
    expect(by_api).to_be_visible()

    # 2) Pure CSS — concise, fine
    by_css = page.locator(
        "[data-test^='product-']:has([data-test='product-name']:text-is('Pliers'))"
    ).first
    expect(by_css).to_be_visible()

    # 3) XPath — most verbose, but useful when you need axes
    by_xpath = page.locator(
        "//span[@data-test='product-name' and normalize-space(text())='Pliers']"
        "/ancestor::a[starts-with(@data-test, 'product-')]"
    ).first
    expect(by_xpath).to_be_visible()


# ---------------------------------------------------------------------------
# 16. Anti-pattern: absolute XPath — DO NOT use
# ---------------------------------------------------------------------------

def test_antipattern_absolute_xpath():
    """
    Absolute XPath breaks the moment anyone reorders elements.
    Shown here as a 'how NOT to' — body left empty on purpose.
    """
    # page.locator("/html/body/div/main/section/div[2]/h1")
    pass


# ---------------------------------------------------------------------------
# 17. Anti-pattern: text_content() + assert
# ---------------------------------------------------------------------------

def test_antipattern_text_content_assert(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # ❌ Wrong — no auto-wait, poor diagnostics
    # title = page.locator("//h1").text_content()
    # assert title == "Practice Software Testing"

    # ✅ Right — expect() auto-waits and produces readable failures
    expect(page.locator("//h1")).to_be_visible()
