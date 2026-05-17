import pytest
from playwright.sync_api import sync_playwright, expect


def test_autosuggest_dropdown(page):
    # Step 1: Open Flipkart
    page.goto("https://www.flipkart.com/")

    # Step 2: Type "smart" in the search box
    search_box = page.locator("input[name='q']")
    search_box.fill("smart")

    # Wait for suggestions to appear
    page.wait_for_timeout(5000)

    # Step 3: Locate all suggestions
    options = page.locator("ul > li")
    count = options.count()
    print("Number of suggested options:", count)

    # Assertion: Expect at least 1 suggestion
    expect(options).to_have_count(count)

    # Step 4: Print the 5th option (index starts from 0)
    if count > 5:
        print("5th option:", options.nth(5).inner_text())

    print("Printing all auto suggestions...")
    for i in range(count):
        print(options.nth(i).text_content())

    # Step 5: Select "smartphone" if it appears
    for i in range(count):
        text = options.nth(i).inner_text()
        if text.strip().lower() == "smartphone":
            options.nth(i).click()
            break

    page.wait_for_timeout(3000)
