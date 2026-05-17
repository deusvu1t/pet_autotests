import playwright
from playwright.sync_api import Page, expect, Selectors


def test_verify_playwright_locators(page: Page):
    # Open local test page
    page.goto("https://testautomationpractice.blogspot.com/p/playwrightpractice.html")

    # 1. get_by_alt_text() - locate image by alt attribute
    logo = page.get_by_alt_text("logo image")
    expect(logo).to_be_visible()

    # 2. get_by_text() - locate by text content (non-interactive element)
    expect(page.get_by_text("List item 1")).to_be_visible()
    expect(page.get_by_text("List item 2 with ")).to_be_visible() # partial text
    expect(page.get_by_text("Special: Unique text identifier")).to_be_visible()

    # 3. get_by_role() - locate by ARIA role
    expect(page.get_by_role("button", name="Primary Action")).to_be_visible()
    expect(page.get_by_role("button", name="Toggle Button")).to_be_visible()
    expect(page.get_by_role("button", name="Div with button role")).to_be_visible()
    expect(page.get_by_role("textbox", name="username")).to_be_visible()
    expect(page.get_by_role("checkbox", name=" Accept terms")).to_be_editable()


    # 4. get_by_label() - form controls
    page.get_by_label("Email Address:").fill("abc@gmail.com")
    page.get_by_label("password").fill("testing")
    page.get_by_label("Your Age:").fill("20")
    page.get_by_label(" Standard").check()
    page.get_by_label(" Express").check()

    # 5. get_by_placeholder() - locate by placeholder
    page.get_by_placeholder("Enter your full name").fill("John Smith")
    page.get_by_placeholder("Phone number (xxx-xxx-xxxx)").fill("123-456-7890")
    page.get_by_placeholder("Type your message here...").fill("this is playwright automation")
    page.get_by_placeholder("Search products...").fill("PW Book")
    page.get_by_role("button", name="Search").click() # here you can use get_by_role()

    # 6. get_by_title() - locate by title attribute
    expect(page.get_by_title("Home page link")).to_have_text("Home")
    expect(page.get_by_title("HyperText Markup Language")).to_have_text("HTML")
    expect(page.get_by_title("Tooltip text")).to_have_text("This text has a tooltip")


    # 7. get_by_test_id() - locate by data-testid attribute

    expect(page.get_by_test_id("profile-name")).to_have_text("John Doe")
    expect(page.get_by_test_id("profile-email")).to_have_text("john.doe@example.com")
    page.get_by_test_id("edit-profile-btn").click()
    page.get_by_test_id("nav-home").click()
    page.get_by_test_id("nav-products").click()
    page.get_by_test_id("nav-contact").click()
