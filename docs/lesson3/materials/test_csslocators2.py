import pytest
from playwright.sync_api import Page, expect


def test_css_locators_in_playwright(page: Page):
    # Launch the URL
    page.goto("https://demowebshop.tricentis.com/")

    # logo (CSS locator)
    relative_logo = page.locator('img[alt="Tricentis Demo Web Shop"]')
    expect(relative_logo).to_be_visible()

    # Products containing "computer" in href attribute
    products = page.locator('h2 > a[href*="computer"]')   # [href*="computer"] mimics XPath contains()
    print("Products count:",products.count())
    expect(products).to_have_count(4)

    print("First Computer product:", products.first.text_content())
    print("N-th Computer product:", products.nth(1).text_content())

    # Capture the product titles and print them
    product_titles = products.all_text_contents()
    print("All computer related product names:", product_titles)

    for pt in product_titles:
        print(pt)

    # Products starting with "/build" in href attribute
    building_products = page.locator('h2 > a[href^="/build"]')   # [href^="/build"] mimics XPath starts-with()
    expect(building_products).to_have_count(3)

    # Register link using CSS selector with exact text match
    register_link = page.locator('a[href="/register"]')
    expect(register_link).to_be_visible()

    # Last social media link (Google+) using :last-child
    google_plus_link = page.locator('.follow-us ul li:last-child')
    expect(google_plus_link).to_have_text("Google+")

    # Second social media link (Twitter) using :nth-child(2)
    twitter_link = page.locator('.follow-us ul li:nth-child(2)')
    expect(twitter_link).to_have_text("Twitter")
