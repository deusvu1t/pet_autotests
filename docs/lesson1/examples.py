"""
Lesson 1 — Playwright + pytest: working examples.

These examples are reference snippets, not part of the project test suite.
Site under test: https://practicesoftwaretesting.com/
Run from this folder:
    pytest examples.py -s -v --headed
"""

from playwright.sync_api import Page, BrowserContext, expect
import pytest


# ---------------------------------------------------------------------------
# 1. Minimal smoke test — URL and title
# ---------------------------------------------------------------------------
# `page: Page` — type-hinted fixture from pytest-playwright.
# A fresh, isolated page is created for every test automatically.
def test_home_url_and_title(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # Web-first assertions: they auto-retry until the condition is met
    # or the default 5s timeout expires. Never replace these with `assert`.
    expect(page).to_have_url("https://practicesoftwaretesting.com/")
    expect(page).to_have_title("Practice Software Testing - Toolshop - v5.0")


# ---------------------------------------------------------------------------
# 2. Multiple assertions on one page
# ---------------------------------------------------------------------------
# Demonstrates the most common locator + expect patterns we will rely on
# later when building the Page Object Model.
def test_home_key_elements_visible(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # Search input is present and ready for interaction.
    search_input = page.get_by_test_id("search-query")
    expect(search_input).to_be_visible()
    expect(search_input).to_be_enabled()

    # Sign-in link in the navbar.
    expect(page.get_by_test_id("nav-sign-in")).to_be_visible()

    # Product grid renders at least one card.
    product_cards = page.locator("[data-test='product-name']")
    expect(product_cards.first).to_be_visible()


# ---------------------------------------------------------------------------
# 3. `expect()` vs raw `assert` — why it matters
# ---------------------------------------------------------------------------
# This test ALSO passes, but if the page is slow it will be flaky.
# Keep this snippet as a "what NOT to do" reference.
def test_bad_assert_example(page: Page):
    page.goto("https://practicesoftwaretesting.com/")

    # BAD: instant check, no waiting. Will fail the moment the network is slow.
    assert "Toolshop" in page.title()

    # GOOD: equivalent web-first assertion with auto-retry.
    expect(page).to_have_title("Practice Software Testing - Toolshop - v5.0")


# ---------------------------------------------------------------------------
# 4. Context isolation — what `context` actually buys you
# ---------------------------------------------------------------------------
# Each test gets its own BrowserContext: separate cookies, storage, cache.
# Even though the browser process is shared, tests cannot leak state.
def test_context_is_isolated(context: BrowserContext, page: Page):
    page.goto("https://practicesoftwaretesting.com/")
    context.add_cookies(
        [
            {
                "name": "demo",
                "value": "from-test-A",
                "domain": "practicesoftwaretesting.com",
                "path": "/",
            }
        ]
    )

    cookies = context.cookies()
    demo_cookie = next(c for c in cookies if c["name"] == "demo")
    assert demo_cookie["value"] == "from-test-A"
    # In any other test, this cookie will not exist — the context is fresh.


# ---------------------------------------------------------------------------
# 5. Custom context options via `browser_context_args` fixture
# ---------------------------------------------------------------------------
# In a real project this lives in conftest.py. Shown here so you see the shape.
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1440, "height": 900},
        "locale": "en-US",
        "ignore_https_errors": True,
    }


# ---------------------------------------------------------------------------
# 6. Tiny Page Object Model preview — what we will build properly in lesson 2
# ---------------------------------------------------------------------------
# Idea: every page has its own class. Tests call methods, not raw selectors.
# Selectors live exactly in one place — easy to maintain.
class HomePage:
    URL = "https://practicesoftwaretesting.com/"

    def __init__(self, page: Page):
        self.page = page
        self.search_input = page.get_by_test_id("search-query")
        self.search_button = page.get_by_test_id("search-submit")

    def open(self) -> "HomePage":
        self.page.goto(self.URL)
        return self

    def search(self, term: str) -> "HomePage":
        self.search_input.fill(term)
        self.search_button.click()
        return self


def test_home_page_object_preview(page: Page):
    home = HomePage(page).open()
    home.search("hammer")

    # Search keeps the term visible in the input field.
    expect(home.search_input).to_have_value("hammer")
