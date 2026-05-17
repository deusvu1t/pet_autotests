import pytest
from playwright.sync_api import Page, expect


def test_xpath_locators(page: Page):
    # Launch the URL
    page.goto("https://demowebshop.tricentis.com/")

    #1. Absolute xpath(full xpath)  - Not recomended
    logo=page.locator("//html/body/div[4]/div[1]/div[1]/div[1]/a/img")
    expect(logo).to_be_visible()

    # 2. Relative xpath :    //tagname[@attribute='value']
    expect(page.locator("//img[@alt='Tricentis Demo Web Shop']")).to_be_visible()
    page.wait_for_timeout(5000)

    #3. xpath with contains()
    products=page.locator("//h2//a[contains(@href,'computer')]")
    products_count=products.count() # 4   counts from 1
    print("Products count:", products_count)
    expect(products).to_have_count(products_count)

    print("First computer product:", products.first.text_content())
    print("Last computer product:", products.last.text_content())
    print("N-th computer product:", products.nth(2).text_content())   #nth() takes index from 0


    product_titles=products.all_text_contents()
    print("Product titles--->:",product_titles)

    print("Printing product tiles using looping statement............")
    for i in product_titles:
        print(i)

    # xpath with starts-with()
    building_products=page.locator("//h2//a[starts-with(@href,'/build')]")
    print("Count of building products:",building_products.count())
    expect(building_products).to_have_count(building_products.count())


    # xpath with text()  - is representing inner text of the element

    registration_link=page.locator("//a[text()='Register']")
    expect(registration_link).to_be_visible()

    page.wait_for_timeout(5000)
    # xpath with last()

    googlepluslink=page.locator("//div[@class='column follow-us']//li[last()]")  # //div[@class='column follow-us']//li[5]
    expect(googlepluslink).to_have_text("Google+")

    # xpath with position()
    twitterlink = page.locator("//div[@class='column follow-us']//li[position()=2]")
    expect(twitterlink ).to_have_text("Twitter")




























