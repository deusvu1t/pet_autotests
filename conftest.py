import os

import pytest
from playwright.sync_api import expect


@pytest.fixture(scope="session", autouse=True)
def configure_expect_timeout():
    expect.set_options(timeout=10_000)


@pytest.fixture(scope="session", autouse=True)
def set_test_id_attribute(playwright):
    playwright.selectors.set_test_id_attribute("data-test")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/136.0.0.0 Safari/537.36"
        ),
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    args = {
        **browser_type_launch_args,
        "args": [
            *browser_type_launch_args.get("args", []),
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ],
    }
    if os.getenv("CI"):
        args["channel"] = "chrome"
    return args
