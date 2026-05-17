import pytest
from playwright.sync_api import Page, expect

def test_built_in_locators(page: Page):
    # 1) Go to URL
    page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")

    # 2) Verify logo is visible
    logo = page.get_by_alt_text("company-branding")
    expect(logo).to_be_visible()

    # 3) Enter username and password
    page.get_by_placeholder("Username").fill("Admin")
    page.get_by_placeholder("Password").fill("admin123")

    # 4) Click on login button
    page.get_by_role("button", name="Login").click()

    # 5) Check Dashboard is visible after login
    expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()
