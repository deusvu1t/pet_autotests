import pytest
from playwright.sync_api import Page, expect

def test_inputbox(page: Page):

    page.goto("https://testautomationpractice.blogspot.com/")
    text_box=page.locator("#name")

    # visibility of teh element and enable or not
    expect(text_box).to_be_visible()
    expect(text_box).to_be_enabled()

    # check the attribute of the elements
    expect(text_box).to_have_attribute("maxlength","15")

    # get an attribute of the element
    maxlength=text_box.get_attribute("maxlength")
    print("Maximum lenght of inputbox:",maxlength )

    # Fill the text
    text_box.fill("John Kenedy")

    # get the input value from inputbox
    enteredvalue=text_box.input_value()
    print("Value entered is:", enteredvalue)

    page.wait_for_timeout(5000)
