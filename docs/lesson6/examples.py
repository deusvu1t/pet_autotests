"""
Lesson 6 — Dropdowns in Playwright.
Target site: https://practicesoftwaretesting.com/

Run from project root:
    pytest docs/lesson6/examples.py -v --headed

All dropdowns on this site are native <select>, so we focus on:
    /            — Sort dropdown
    /auth/register — Country dropdown (many options)
    /contact     — Subject dropdown (closed set)
"""

from playwright.sync_api import Page, expect


BASE_URL = "https://practicesoftwaretesting.com"


# ---------------------------------------------------------------------------
# 1. select_option — three ways
# ---------------------------------------------------------------------------

def test_select_by_label(page: Page):
    page.goto(f"{BASE_URL}/")
    sort = page.get_by_test_id("sort")
    sort.select_option(label="Name (A - Z)")


def test_select_by_value(page: Page):
    """
    `value` is the HTML attribute on <option>, NOT the displayed text.
    On this site values look like 'name,asc'. Check DevTools first.
    """
    page.goto(f"{BASE_URL}/")
    sort = page.get_by_test_id("sort")
    sort.select_option(value="name,asc")


def test_select_by_index(page: Page):
    """
    Index starts from 0 — and includes any placeholder option.
    Use only when label/value are unreliable.
    """
    page.goto(f"{BASE_URL}/")
    sort = page.get_by_test_id("sort")
    sort.select_option(index=1)


# ---------------------------------------------------------------------------
# 2. Reading dropdown contents
# ---------------------------------------------------------------------------

def test_read_all_sort_options(page: Page):
    page.goto(f"{BASE_URL}/")
    sort = page.get_by_test_id("sort")

    options = [o.strip() for o in sort.locator("option").all_text_contents()]

    assert "Name (A - Z)" in options
    assert "Price (Low - High)" in options
    assert "Price (High - Low)" in options


def test_sort_options_exact_list(page: Page):
    """
    Strict check: the full list of options must match.
    Good for closed sets where adding a new option = a real change worth catching.
    """
    page.goto(f"{BASE_URL}/")
    sort = page.get_by_test_id("sort")

    expect(sort.locator("option")).to_have_text(
        [
            "Name (A - Z)",
            "Name (Z - A)",
            "Price (High - Low)",
            "Price (Low - High)",
        ]
    )


def test_sort_options_count(page: Page):
    page.goto(f"{BASE_URL}/")
    sort = page.get_by_test_id("sort")

    expect(sort.locator("option")).to_have_count(4)


# ---------------------------------------------------------------------------
# 3. Reading the current selected value
# ---------------------------------------------------------------------------

def test_current_value(page: Page):
    page.goto(f"{BASE_URL}/")
    sort = page.get_by_test_id("sort")

    sort.select_option(value="price,asc")

    expect(sort).to_have_value("price,asc")
    # If you need the visible label of the selected option:
    selected_label = sort.locator("option:checked").text_content()
    assert selected_label and selected_label.strip() == "Price (Low - High)"


# ---------------------------------------------------------------------------
# 4. Country dropdown — large set, check specific options
# ---------------------------------------------------------------------------

def test_country_dropdown_has_specific_countries(page: Page):
    page.goto(f"{BASE_URL}/auth/register")
    country = page.get_by_label("Country")

    options = [o.strip() for o in country.locator("option").all_text_contents()]

    # On a large dropdown, checking exact list is fragile.
    # Better: assert specific values exist.
    assert "United States" in options
    assert "Canada" in options
    assert "Germany" in options


def test_country_dropdown_has_many_options(page: Page):
    """
    Soft check on count — countries don't change often, but the exact
    number is fragile. Use a lower bound instead.
    """
    page.goto(f"{BASE_URL}/auth/register")
    country = page.get_by_label("Country")

    option_count = country.locator("option").count()
    assert option_count > 100, f"Expected >100 countries, got {option_count}"


# ---------------------------------------------------------------------------
# 5. Contact subject — closed set, full match
# ---------------------------------------------------------------------------

def test_contact_subject_options(page: Page):
    page.goto(f"{BASE_URL}/contact")
    subject = page.get_by_label("Subject")

    # Subject is a closed business-driven set — check exact list.
    expect(subject.locator("option")).to_contain_text(
        [
            "Customer service",
            "Webmaster",
            "Warranty",
            "Return",
            "Payments",
        ]
    )


# ---------------------------------------------------------------------------
# 6. Verifying sort actually works — alphabetical
# ---------------------------------------------------------------------------

def test_sort_by_name_az_actually_sorts(page: Page):
    page.goto(f"{BASE_URL}/")
    sort = page.get_by_test_id("sort")

    sort.select_option(label="Name (A - Z)")

    # Wait for the grid to re-render after the request
    first_card_name = page.locator("[data-test='product-name']").first
    expect(first_card_name).to_be_visible()

    names = page.locator("[data-test='product-name']").all_text_contents()
    names = [n.strip() for n in names]

    assert names == sorted(names), f"Products not sorted A-Z: {names}"


# ---------------------------------------------------------------------------
# 7. Verifying sort by price — needs parsing
# ---------------------------------------------------------------------------

def parse_price(text: str) -> float:
    return float(text.replace("$", "").strip())


def test_sort_by_price_low_to_high_actually_sorts(page: Page):
    page.goto(f"{BASE_URL}/")
    sort = page.get_by_test_id("sort")

    # Get a baseline before sorting to use as a wait signal
    first_card = page.locator("[data-test='product-name']").first
    old_text = first_card.text_content()

    sort.select_option(label="Price (Low - High)")
    expect(first_card).not_to_have_text(old_text or "")  # wait for re-render

    prices_text = page.locator("[data-test='product-price']").all_text_contents()
    prices = [parse_price(p) for p in prices_text]

    assert prices == sorted(prices), f"Not sorted ascending: {prices}"


def test_sort_by_price_high_to_low_actually_sorts(page: Page):
    page.goto(f"{BASE_URL}/")
    sort = page.get_by_test_id("sort")

    first_card = page.locator("[data-test='product-name']").first
    old_text = first_card.text_content()

    sort.select_option(label="Price (High - Low)")
    expect(first_card).not_to_have_text(old_text or "")

    prices_text = page.locator("[data-test='product-price']").all_text_contents()
    prices = [parse_price(p) for p in prices_text]

    assert prices == sorted(prices, reverse=True), f"Not sorted descending: {prices}"


# ---------------------------------------------------------------------------
# 8. Multi-select example — synthetic (this site has no multi-select)
# ---------------------------------------------------------------------------

def test_multi_select_pattern_example():
    """
    Reference pattern — practicesoftwaretesting.com has no multi-select,
    but here's how it works on sites that do.

    page.get_by_label("Colors").select_option(["Red", "Blue", "Green"])
    page.get_by_label("Colors").select_option(value=["red", "blue"])

    # Clear all selections:
    page.get_by_label("Colors").select_option([])
    """
    pass


# ---------------------------------------------------------------------------
# 9. Custom dropdown (combobox) — reference pattern
# ---------------------------------------------------------------------------

def test_custom_dropdown_pattern_example():
    """
    Reference pattern for ARIA combobox / listbox dropdowns
    (not present on this site, common on React / Material UI sites).

    # Open the dropdown
    page.get_by_role("combobox", name="Country").click()

    # Click the option
    page.get_by_role("option", name="United States").click()

    # Verify
    expect(page.get_by_role("combobox", name="Country")).to_contain_text(
        "United States"
    )
    """
    pass


# ---------------------------------------------------------------------------
# 10. Anti-pattern: print instead of assert
# ---------------------------------------------------------------------------

def test_antipattern_print_check(page: Page):
    page.goto(f"{BASE_URL}/")
    sort = page.get_by_test_id("sort")
    options = sort.locator("option").all_text_contents()

    # ❌ Test always passes, no real check
    # if options == sorted(options):
    #     print("Sorted!")
    # else:
    #     print("Not sorted!")

    # ✅
    options = [o.strip() for o in options]
    # Don't assert sorted here — these are sort-mode labels, not data
    assert "Name (A - Z)" in options


# ---------------------------------------------------------------------------
# 11. Anti-pattern: wait_for_timeout after select_option
# ---------------------------------------------------------------------------

def test_antipattern_wait_for_timeout(page: Page):
    page.goto(f"{BASE_URL}/")
    sort = page.get_by_test_id("sort")
    first_card = page.locator("[data-test='product-name']").first

    # ❌
    # sort.select_option(label="Name (Z - A)")
    # page.wait_for_timeout(3000)

    # ✅ Wait for actual UI change
    old_text = first_card.text_content()
    sort.select_option(label="Name (Z - A)")
    expect(first_card).not_to_have_text(old_text or "")
