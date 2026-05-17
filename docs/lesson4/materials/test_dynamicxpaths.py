'''
//button[text()='START' or text()='STOP']
//button[@name='start' or @name='stop']
//button[contains(@name,'st')]
//button[starts-with(@name,'st')]


'''


import pytest
from playwright.sync_api import Page, expect
import re

# using xpath...........

# def test_handle_dynamic_elements(page: Page):
#     page.goto("https://testautomationpractice.blogspot.com/")
#
#     for i in range(5):
#         button=page.locator("//button[text()='START' or text()='STOP']")
#         button.click()
#         page.wait_for_timeout(2000)


# using css...............
# def test_handle_dynamic_elements_css(page: Page):
#     page.goto("https://testautomationpractice.blogspot.com/")
#
#     for i in range(5):
#         button=page.locator("button[name^='st']")
#         button.click()
#         page.wait_for_timeout(2000)

# using playwright locator...............

def test_handle_dynamic_elements_css(page: Page):
    page.goto("https://testautomationpractice.blogspot.com/")

    for i in range(5):
        button=page.get_by_role("button",name=re.compile(r'ST.*'))
        button.click()
        page.wait_for_timeout(2000)






