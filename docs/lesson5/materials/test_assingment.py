import pytest
from playwright.sync_api import Page, expect

def test_elements(page: Page):
    page.goto("https://practice-automation.com/form-fields/")

    # 1. Check visibility and enabled state - Name & Password, then fill the text

    #name
    name = page.locator("#name-input")
    expect(name).to_be_visible()
    expect(name).to_be_enabled()
    name.fill("John")

    #password
    password=page.locator("input[type='password']")
    expect(password).to_be_visible()
    expect(password).to_be_enabled()
    password.fill("Johnxyz")

    page.wait_for_timeout(3000)

    # 2. Count number of favorite drinks and select all the favorite drinks and assert each check box is selected

    drinks_labels = ['Water', 'Milk', 'Coffee', 'Wine', 'Ctrl-Alt-Delight']
    favoritedrinks_checkboxes = [page.get_by_label(drink) for drink in drinks_labels]
    print("total number of favorite drinks:", len(favoritedrinks_checkboxes))

    for checkbox in favoritedrinks_checkboxes:
        checkbox.check()
        expect(checkbox).to_be_checked()

    page.wait_for_timeout(3000)


    # 3. Check favorite color "Green" radio button by choice

    color_labels=['Red','Blue','Yellow','Green']
    choose_color = "Green"

    for colorlabel in color_labels:
        if colorlabel == choose_color:
            radiobutton = page.get_by_label(colorlabel)
            radiobutton.check()
            expect(radiobutton).to_be_checked()

    page.wait_for_timeout(3000)

 #4 . Print all the automation tools

    automationtools=page.locator("form[id='feedbackForm'] ul li")  # css for all the automation tools elements
    expect(automationtools).to_have_count(5)

    automationtools_texts=automationtools.all_text_contents()

    for tool in automationtools_texts:
        print(tool)

    page.wait_for_timeout(5000)