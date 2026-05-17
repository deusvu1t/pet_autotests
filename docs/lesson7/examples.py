"""
Lesson 7 — Text extraction methods and custom dropdowns.
Target site: https://practicesoftwaretesting.com/

Run from project root:
    pytest docs/lesson7/examples.py -v --headed

Topics:
    1-4   inner_text vs text_content (single)
    5-7   all_inner_texts vs all_text_contents (multiple)
    8-9   all() — list of Locators
    10-12 Custom dropdowns (Bootstrap-style user menu after login)
    13    Autosuggest pattern (reference — site has no autosuggest)
    14-16 Anti-patterns with fixes
"""

from playwright.sync_api import Page, expect


BASE_URL = "https://practicesoftwaretesting.com"
DEMO_USER = {"email": "customer@practicesoftwaretesting.com", "password": "welcome01"}


# ---------------------------------------------------------------------------
# 1. inner_text() — clean visible text from one element
# ---------------------------------------------------------------------------

def test_inner_text_clean(page: Page):
    page.goto(f"{BASE_URL}/")
    first_name = page.locator("[data-test='product-name']").first

    name = first_name.inner_text()
    assert name and not name.startswith("\n"), "inner_text strips whitespace"


# ---------------------------------------------------------------------------
# 2. text_content() — raw text with whitespace
# ---------------------------------------------------------------------------

def test_text_content_raw(page: Page):
    page.goto(f"{BASE_URL}/")
    first_name = page.locator("[data-test='product-name']").first

    # text_content() may include whitespace/newlines depending on HTML
    raw = first_name.text_content()
    assert raw is not None  # text_content can return None for empty elements


# ---------------------------------------------------------------------------
# 3. text_content() returns None for empty elements
# ---------------------------------------------------------------------------

def test_text_content_none_pitfall(page: Page):
    page.goto(f"{BASE_URL}/")

    empty = page.locator("body").locator("nonexistent-tag")
    text = empty.text_content() if empty.count() else None
    # NEVER call .strip() on text_content() without a None check.
    safe = (text or "").strip()
    assert safe == ""


# ---------------------------------------------------------------------------
# 4. Best practice: expect() for text checks
# ---------------------------------------------------------------------------

def test_expect_for_text_validation(page: Page):
    page.goto(f"{BASE_URL}/")
    first_name = page.locator("[data-test='product-name']").first

    # ❌ Manual: dig text out + assert — no auto-wait
    # assert first_name.inner_text() == "Combination Pliers"

    # ✅ expect — waits, normalizes whitespace, clear diagnostics on failure
    expect(first_name).to_have_text("Combination Pliers")


# ---------------------------------------------------------------------------
# 5. all_inner_texts() — clean list of strings
# ---------------------------------------------------------------------------

def test_all_inner_texts(page: Page):
    page.goto(f"{BASE_URL}/")
    names_loc = page.locator("[data-test='product-name']")
    names_loc.first.wait_for()

    names = names_loc.all_inner_texts()
    assert all(n == n.strip() for n in names), "already trimmed"
    assert len(names) >= 9


# ---------------------------------------------------------------------------
# 6. all_text_contents() — raw, with whitespace
# ---------------------------------------------------------------------------

def test_all_text_contents_raw(page: Page):
    page.goto(f"{BASE_URL}/")
    names_loc = page.locator("[data-test='product-name']")
    names_loc.first.wait_for()

    # ❌ Common pattern that lesson 7 replaces
    names_old = [n.strip() for n in names_loc.all_text_contents()]

    # ✅ Same thing, one line
    names_new = names_loc.all_inner_texts()

    assert names_old == names_new


# ---------------------------------------------------------------------------
# 7. Sorting product names — use all_inner_texts
# ---------------------------------------------------------------------------

def test_names_sorted(page: Page):
    page.goto(f"{BASE_URL}/")
    sort = page.get_by_test_id("sort")

    first = page.locator("[data-test='product-name']").first
    old = first.inner_text()
    sort.select_option(label="Name (A - Z)")
    expect(first).not_to_have_text(old)

    names = page.locator("[data-test='product-name']").all_inner_texts()
    assert names == sorted(names)


# ---------------------------------------------------------------------------
# 8. all() — convert Locator to list[Locator] for per-element actions
# ---------------------------------------------------------------------------

def test_all_for_per_element_actions(page: Page):
    page.goto(f"{BASE_URL}/")
    cards_loc = page.locator("a[data-test^='product-']")
    cards_loc.first.wait_for()

    cards = cards_loc.all()

    # Different actions per card — useful when text isn't enough
    for i, card in enumerate(cards[:3]):
        name = card.locator("[data-test='product-name']").inner_text()
        price = card.locator("[data-test='product-price']").inner_text()
        assert name and price, f"Card {i} missing name or price"


# ---------------------------------------------------------------------------
# 9. all() pitfall: no auto-wait
# ---------------------------------------------------------------------------

def test_all_does_not_wait(page: Page):
    page.goto(f"{BASE_URL}/")

    # ❌ all() returns snapshot — may be empty if elements still loading
    # cards = page.locator(".product").all()

    # ✅ Wait for at least one, then snapshot
    products_loc = page.locator("a[data-test^='product-']")
    products_loc.first.wait_for()
    cards = products_loc.all()

    assert len(cards) >= 9


# ---------------------------------------------------------------------------
# 10. Bootstrap dropdown — user menu after login
# ---------------------------------------------------------------------------

def test_user_menu_opens_after_login(page: Page):
    page.goto(f"{BASE_URL}/auth/login")
    page.get_by_label("Email address").fill(DEMO_USER["email"])
    page.get_by_label("Password").fill(DEMO_USER["password"])
    page.get_by_role("button", name="Login").click()

    expect(page).to_have_url(lambda u: "/account" in u)

    # The "Hi, <user>" button in the header — a Bootstrap dropdown trigger
    menu_trigger = page.get_by_test_id("nav-menu")
    menu_trigger.click()

    # Wait for an item to appear — proves the menu actually opened
    sign_out = page.get_by_test_id("nav-sign-out")
    expect(sign_out).to_be_visible()


# ---------------------------------------------------------------------------
# 11. Bootstrap dropdown — click an item
# ---------------------------------------------------------------------------

def test_sign_out_via_user_menu(page: Page):
    page.goto(f"{BASE_URL}/auth/login")
    page.get_by_label("Email address").fill(DEMO_USER["email"])
    page.get_by_label("Password").fill(DEMO_USER["password"])
    page.get_by_role("button", name="Login").click()
    expect(page).to_have_url(lambda u: "/account" in u)

    page.get_by_test_id("nav-menu").click()
    page.get_by_test_id("nav-sign-out").click()

    expect(page).to_have_url(lambda u: "/auth/login" in u)


# ---------------------------------------------------------------------------
# 12. Reading the cart counter — inner_text on a small badge
# ---------------------------------------------------------------------------

def test_cart_counter_starts_at_zero(page: Page):
    page.goto(f"{BASE_URL}/")
    counter = page.get_by_test_id("cart-quantity")

    # inner_text — visible badge value
    value = counter.inner_text()
    assert value == "0"

    # Equivalent expect (preferred for the actual test)
    expect(counter).to_have_text("0")


# ---------------------------------------------------------------------------
# 13. Autosuggest pattern — REFERENCE only (this site has no autosuggest)
# ---------------------------------------------------------------------------

def test_autosuggest_pattern_reference():
    """
    For an autosuggest input (Flipkart, Google, Amazon):

        search = page.get_by_role("searchbox")
        search.press_sequentially("smart")   # NOT fill — each keystroke triggers

        suggestion = page.get_by_role("option", name="smartphone")
        expect(suggestion).to_be_visible()
        suggestion.click()

    press_sequentially is the ONE case where it beats fill().
    """
    pass


# ---------------------------------------------------------------------------
# 14. Anti-pattern: expect(loc).to_have_count(loc.count())
# ---------------------------------------------------------------------------

def test_antipattern_count_tautology(page: Page):
    page.goto(f"{BASE_URL}/")
    products = page.locator("a[data-test^='product-']")
    products.first.wait_for()

    # ❌ Pointless — comparing a number to itself
    # count = products.count()
    # expect(products).to_have_count(count)

    # ✅ Compare to an EXPECTED value
    expect(products).to_have_count(9)


# ---------------------------------------------------------------------------
# 15. Anti-pattern: wait_for_timeout after dropdown click
# ---------------------------------------------------------------------------

def test_antipattern_timeout_after_click(page: Page):
    page.goto(f"{BASE_URL}/auth/login")
    page.get_by_label("Email address").fill(DEMO_USER["email"])
    page.get_by_label("Password").fill(DEMO_USER["password"])
    page.get_by_role("button", name="Login").click()
    expect(page).to_have_url(lambda u: "/account" in u)

    menu_trigger = page.get_by_test_id("nav-menu")
    menu_trigger.click()

    # ❌
    # page.wait_for_timeout(3000)

    # ✅ Wait for an item that proves the menu opened
    expect(page.get_by_test_id("nav-sign-out")).to_be_visible()


# ---------------------------------------------------------------------------
# 16. Anti-pattern: print "check" instead of assert
# ---------------------------------------------------------------------------

def test_antipattern_print_check(page: Page):
    page.goto(f"{BASE_URL}/")
    products = page.locator("[data-test='product-name']")
    products.first.wait_for()

    # ❌ Test always passes
    # print("Number of products:", products.count())

    # ✅ Assert something meaningful
    assert products.count() >= 9
