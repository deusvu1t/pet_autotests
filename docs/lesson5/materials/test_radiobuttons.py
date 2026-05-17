import pytest
from playwright.sync_api import Page, expect


def test_radio_buttons(page:Page):
    page.goto("https://testautomationpractice.blogspot.com/")

    male_radio=page.locator("#male")

    # visibility of teh element and enable or not
    expect(male_radio).to_be_visible()
    expect(male_radio).to_be_enabled()

    # Male radio button should not be checked ( default)
    expect(male_radio).not_to_be_checked()

    # Select/Check radio button - action
    male_radio.check()

    # Male radio button should not be checked ( default)
    expect(male_radio).to_be_checked()

    page.wait_for_timeout(5000)


