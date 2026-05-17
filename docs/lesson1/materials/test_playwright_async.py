# Pre-requisite for Asynchrouns execution
# install  pytest-asyncio
# command:   pip install pytest-asyncio

from playwright.async_api import async_playwright,Page, expect
import pytest

@pytest.mark.asyncio
async def test_verifyPageUrl_async():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  #  headed mode
        mypage = await browser.new_page()
        await mypage.goto("https://demowebshop.tricentis.com/")
        await expect(mypage).to_have_url("https://demowebshop.tricentis.com/")
        await browser.close()

