import pytest
from playwright.sync_api import sync_playwright, expect, Page


def test_bootstrapdropdown(page : Page):
    # Launch the URL
    page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")

    # Login steps
    page.locator('input[name="username"]').fill('Admin')
    page.locator('input[name="password"]').fill('admin123')
    page.locator('button[type="submit"]').click()

    page.wait_for_timeout(3000)

    # click on PIM
    page.get_by_text('PIM').click()


    # click on the Job title dropdown
    page.locator("form i").nth(2).click() # this will open options from the dropdown
    page.wait_for_timeout(3000)

    # capture all teh options from dropdown
    options=page.locator("div[role='listbox'] span")

    count=options.count()  # get the cout of options
    print("Number of options in the dropdown:", count)

    expect(options).to_have_count(count) # assertion for counting the options

    page.wait_for_timeout(3000)

    # Print all teh options
    print("All the options from the dropdown===>", options.all_text_contents())

    # Print all teh options text using loop
    # for i in range(count):
    #     print(options.nth(i).text_content())

    # select/click on specific option
    for i in range(count):
        text=options.nth(i).inner_text()
        if text=='Finance Manager':
            print("Matching success.....")
            options.nth(i).click()
            break

    page.wait_for_timeout(5000)




