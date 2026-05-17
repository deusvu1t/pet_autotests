import pytest
from playwright.sync_api import sync_playwright, expect, Page


def test_single_select_dropdown(page: Page):
    page.goto("https://testautomationpractice.blogspot.com/")

    # 3 ways to select option from the dropdown
    #page.locator("#country").select_option("India")  # by label
    page.locator("#country").select_option(label="India")  # by label

    selected_value = page.locator("#country").input_value() # capture selected option
    print("Selected Value:", selected_value)

    #page.locator("#country").select_option("germany")  #by value
    #page.locator("#country").select_option(value="germany")  # by value

    #page.locator("#country").select_option(index=3)   # by index  # index starts from 0

    # check number of options in dropdown

    dropdown_options=page.locator("#country>option")
    expect(dropdown_options).to_have_count(10)

    options_text=[text.strip() for text in dropdown_options.all_text_contents()]
    print(options_text)

    # print countries using loop
    for option in options_text:
        print(option)


    page.wait_for_timeout(5000)

