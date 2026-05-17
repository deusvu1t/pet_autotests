import pytest
from playwright.sync_api import Page, expect


def test_checkbox(page:Page):
    page.goto("https://testautomationpractice.blogspot.com/")

    #1. select specific checkbox (Sunday)
    # sunday_checkbox=page.get_by_label("Sunday")
    # sunday_checkbox.check()
    # expect(sunday_checkbox).to_be_checked()
    # page.wait_for_timeout(5000)

    #2. count number of check boxes

    #step1:
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    checkboxes=[]

    #step2
    # for day in days:
    #     checkbox=page.get_by_label(day)
    #     checkboxes.append(checkbox)

    checkboxes=[page.get_by_label(day) for day in days]
    print("total number of checkboxes:", len(checkboxes))


    #3 . select all the checkboxes and assert each check box is selected
    # for checkbox in checkboxes:
    #     checkbox.check()
    #     expect(checkbox).to_be_checked()
    #
    # page.wait_for_timeout(5000)


    #4. check last 3 checkboxes
    # for checkbox in checkboxes[-3:]:
    #     checkbox.uncheck()
    #     expect(checkbox).not_to_be_checked()
    #
    # page.wait_for_timeout(5000)

    #5. Toggle checkboxes.

    for checkbox in checkboxes:
        if checkbox.is_checked():
            checkbox.uncheck()
            expect(checkbox).not_to_be_checked()
        else:
            checkbox.check()
            expect(checkbox).to_be_checked()

    page.wait_for_timeout(5000)

    #6. Randomly check checkboxes - check 1,3 6 checkboxes
    # indexes=[1,3,6]
    #
    # for i in indexes:
    #     checkboxes[i].check()
    #     expect(checkboxes[i]).to_be_checked()
    #
    # page.wait_for_timeout(5000)

    #7. select checkbox based on the label/input value by choice
    weekday="Friday"

    for label in days:
        if label==weekday:
            checkbox=page.get_by_label(label)
            checkbox.check()
            expect(checkbox).to_be_checked()

    page.wait_for_timeout(5000)



















