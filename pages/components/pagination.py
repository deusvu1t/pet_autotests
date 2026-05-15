from playwright.sync_api import Locator, Page


class Pagination:
    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def root(self) -> Locator:
        return self.page.locator("//*[contains(@class, 'pagination')]")

    @property
    def buttons(self) -> Locator:
        return self.root.locator("//li")

    @property
    def next_button(self) -> Locator:
        return self.buttons.last

    @property
    def prev_button(self) -> Locator:
        return self.buttons.first

    def go_to_page(self, number: int) -> None:
        return self.buttons.locator(f"//a[normalize-space(text())='{number}']").click()

    def go_to_next_page(self) -> None:
        self.next_button.locator("a").click()

    def go_to_last_page(self) -> None:
        return self.root.locator("//li[last()-1]/a").click()

    def current_page(self) -> int:
        number_of_page = self.root.locator(
            "//li[contains(@class,'active')]"
        ).text_content()

        if number_of_page is None:
            raise ValueError("Active page not found")

        return int(number_of_page.strip())
