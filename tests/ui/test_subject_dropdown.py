import pytest
from playwright.sync_api import Page

from pages.contact_page import ContactPage


@pytest.mark.ui
@pytest.mark.regression
def test_subject_dropdown_has_expected_options(page: Page):
    contact_page = ContactPage(page).open()

    actual_options = contact_page.subject_options()

    expected_options = {
        "Select a subject *",
        "Customer service",
        "Webmaster",
        "Return",
        "Payments",
        "Warranty",
        "Status of my order",
    }

    assert set(actual_options) == expected_options
