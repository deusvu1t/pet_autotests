"""
Lesson 5 — Form elements in Playwright.
Target site: https://practicesoftwaretesting.com/

Run from project root:
    pytest docs/lesson5/examples.py -v --headed

Forms practiced:
    /auth/register  — registration form (inputs, select, validation)
    /contact        — contact form (textarea, select, file upload)
    /               — home page filters (checkboxes batch)
"""

from playwright.sync_api import Page, expect


BASE_URL = "https://practicesoftwaretesting.com"


# ---------------------------------------------------------------------------
# 1. Text inputs — fill, input_value, expect
# ---------------------------------------------------------------------------

def test_fill_and_read_back(page: Page):
    page.goto(f"{BASE_URL}/auth/login")

    email = page.get_by_label("Email address")

    email.fill("user@example.com")

    # UI assertion — use expect, it auto-waits
    expect(email).to_have_value("user@example.com")

    # Pure data — use input_value()
    value = email.input_value()
    assert value == "user@example.com"


# ---------------------------------------------------------------------------
# 2. Attributes — get_attribute vs to_have_attribute
# ---------------------------------------------------------------------------

def test_attribute_checks(page: Page):
    page.goto(f"{BASE_URL}/auth/login")

    password = page.get_by_label("Password")

    # UI assertion
    expect(password).to_have_attribute("type", "password")

    # Get value to use in code
    placeholder = password.get_attribute("placeholder")
    print(f"Password placeholder: {placeholder}")


# ---------------------------------------------------------------------------
# 3. State assertions
# ---------------------------------------------------------------------------

def test_state_assertions(page: Page):
    page.goto(f"{BASE_URL}/auth/login")

    email = page.get_by_label("Email address")
    submit = page.get_by_role("button", name="Login")

    expect(email).to_be_visible()
    expect(email).to_be_enabled()
    expect(email).to_be_editable()
    expect(email).to_be_empty()

    expect(submit).to_be_visible()
    expect(submit).to_be_enabled()


# ---------------------------------------------------------------------------
# 4. clear() and press()
# ---------------------------------------------------------------------------

def test_clear_and_press(page: Page):
    page.goto(f"{BASE_URL}/")

    search = page.get_by_test_id("search-query")

    search.fill("hammer")
    expect(search).to_have_value("hammer")

    search.clear()
    expect(search).to_have_value("")

    # Type and submit via Enter
    search.fill("pliers")
    search.press("Enter")
    expect(page.get_by_test_id("search-caption")).to_contain_text("pliers")


# ---------------------------------------------------------------------------
# 5. Checkboxes — single
# ---------------------------------------------------------------------------

def test_checkbox_single(page: Page):
    page.goto(f"{BASE_URL}/")

    hand_tools = page.get_by_role("checkbox", name="Hand Tools")

    expect(hand_tools).not_to_be_checked()
    hand_tools.check()
    expect(hand_tools).to_be_checked()

    hand_tools.uncheck()
    expect(hand_tools).not_to_be_checked()


# ---------------------------------------------------------------------------
# 6. Checkboxes — batch via iteration over labels
# ---------------------------------------------------------------------------

def test_checkbox_batch_check_all(page: Page):
    page.goto(f"{BASE_URL}/")

    categories = ["Hand Tools", "Power Tools", "Other"]

    for category in categories:
        checkbox = page.get_by_role("checkbox", name=category)
        checkbox.check()
        expect(checkbox).to_be_checked()


def test_checkbox_toggle_pattern(page: Page):
    """
    Classic pattern from the lesson — toggle each checkbox depending
    on its current state. Reads is_checked() (returns bool, not a Locator).
    """
    page.goto(f"{BASE_URL}/")

    categories = ["Hand Tools", "Power Tools"]

    for category in categories:
        checkbox = page.get_by_role("checkbox", name=category)
        if checkbox.is_checked():
            checkbox.uncheck()
            expect(checkbox).not_to_be_checked()
        else:
            checkbox.check()
            expect(checkbox).to_be_checked()


# ---------------------------------------------------------------------------
# 7. Select dropdown — three ways
# ---------------------------------------------------------------------------

def test_select_option_by_label(page: Page):
    page.goto(f"{BASE_URL}/")

    sort = page.get_by_test_id("sort")
    sort.select_option(label="Name (A - Z)")


def test_select_option_by_value(page: Page):
    page.goto(f"{BASE_URL}/")

    sort = page.get_by_test_id("sort")
    # `value` is the HTML attribute on <option>, NOT the displayed text
    # Check DevTools first — values on this site look like "name,asc"
    sort.select_option(value="name,asc")


def test_select_read_options(page: Page):
    page.goto(f"{BASE_URL}/")

    sort = page.get_by_test_id("sort")
    options = sort.locator("option").all_text_contents()
    assert "Name (A - Z)" in options
    assert "Price (Low - High)" in options


# ---------------------------------------------------------------------------
# 8. Registration form — full POM-style flow
# ---------------------------------------------------------------------------

def test_register_form_fields_present(page: Page):
    """
    Check that the registration form has the right field types.
    This is what 'test the form contract' looks like.
    """
    page.goto(f"{BASE_URL}/auth/register")

    first_name = page.get_by_label("First name")
    email = page.get_by_label("Email address")
    password = page.get_by_label("Password")

    expect(first_name).to_have_attribute("type", "text")
    expect(email).to_have_attribute("type", "email")
    expect(password).to_have_attribute("type", "password")


def test_register_validation_required_fields(page: Page):
    """
    Submit empty form → expect inline validation messages.
    The site uses Angular reactive forms — error nodes appear under inputs.
    """
    page.goto(f"{BASE_URL}/auth/register")

    page.get_by_role("button", name="Register").click()

    # Several validation messages should appear — at least one is enough to assert
    error = page.get_by_test_id("register-error")
    # If error container doesn't show, page-level validation may use aria-invalid:
    first_name = page.get_by_label("First name")
    # Soft-check: either aria-invalid OR visible error text
    is_invalid = first_name.get_attribute("aria-invalid")
    # Demonstrate both styles of validation check:
    if is_invalid == "true":
        expect(first_name).to_have_attribute("aria-invalid", "true")
    else:
        # Fall back to looking for an error text node nearby
        expect(error.first).to_be_visible()


# ---------------------------------------------------------------------------
# 9. Textarea — contact form message field
# ---------------------------------------------------------------------------

def test_textarea(page: Page):
    page.goto(f"{BASE_URL}/contact")

    message = page.get_by_label("Message")

    long_text = "Hello,\nThis is line two.\nAnd line three."
    message.fill(long_text)

    expect(message).to_have_value(long_text)


# ---------------------------------------------------------------------------
# 10. File upload — set_input_files
# ---------------------------------------------------------------------------

def test_file_upload(page: Page, tmp_path):
    """
    tmp_path is a pytest fixture — gives a temp directory per test.
    """
    page.goto(f"{BASE_URL}/contact")

    # Create a small fake file
    sample = tmp_path / "sample.txt"
    sample.write_text("This is a test attachment.")

    file_input = page.locator("input[type='file']")
    file_input.set_input_files(str(sample))

    # Browsers don't expose the file path back — but we can check input_value
    # which usually contains 'C:\\fakepath\\<filename>' or similar.
    # Better: check that the form is ready to submit (no file-related error).
    expect(file_input).not_to_be_empty()


# ---------------------------------------------------------------------------
# 11. Anti-pattern: assert against UI state
# ---------------------------------------------------------------------------

def test_antipattern_assert_against_ui(page: Page):
    page.goto(f"{BASE_URL}/auth/login")

    email = page.get_by_label("Email address")
    email.fill("user@test.com")

    # ❌ No auto-wait, bad diagnostics on failure
    # assert email.input_value() == "user@test.com"

    # ✅ Auto-waits, clear failure messages
    expect(email).to_have_value("user@test.com")


# ---------------------------------------------------------------------------
# 12. Anti-pattern: press_sequentially where fill works
# ---------------------------------------------------------------------------

def test_antipattern_press_sequentially(page: Page):
    page.goto(f"{BASE_URL}/")

    search = page.get_by_test_id("search-query")

    # ❌ Slow, flaky, no real reason
    # search.press_sequentially("hammer", delay=100)

    # ✅ Fast and reliable
    search.fill("hammer")
    expect(search).to_have_value("hammer")


# ---------------------------------------------------------------------------
# 13. Anti-pattern: wait_for_timeout after a fill
# ---------------------------------------------------------------------------

def test_antipattern_sleep_after_fill(page: Page):
    page.goto(f"{BASE_URL}/auth/login")

    page.get_by_label("Email address").fill("user@test.com")
    page.get_by_label("Password").fill("welcome01")

    # ❌ Unnecessary
    # page.wait_for_timeout(3000)

    page.get_by_role("button", name="Login").click()

    # expect() auto-waits up to 5s for the URL change
    expect(page).to_have_url(lambda url: "/account" in url)
