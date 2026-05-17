from playwright.sync_api import sync_playwright, expect

def test_product_sort_and_print_prices(page):
    # Navigate to the URL
    page.goto("https://www.bstackdemo.com/")

    # Locate "Order by" dropdown
    order_by_dropdown = page.locator("div.sort>select")
    expect(order_by_dropdown).to_be_visible()   # Assert dropdown is visible
    expect(order_by_dropdown).to_be_enabled()   # Assert dropdown is enabled

    # Select "Lowest to highest" option
    order_by_dropdown.select_option(label="Lowest to highest")

    # Wait for sorting to reflect
    page.wait_for_timeout(3000)

    # Get all product price and name elements
    price_elements = page.locator("div.val")
    name_elements = page.locator("p.shelf-item__title")

    prices = price_elements.all_text_contents()
    names = name_elements.all_text_contents()


    # Print product names and prices
    print("Printing Product Names along with their Prices.......")
    for i in range(len(names)):
        print(f"{names[i]} : {prices[i]}")

    # Print lowest and highest priced products
    print(f"Lowest Priced Product: {names[0]} : {prices[0]}")
    print(f"Highest Priced Product: {names[-1]} : {prices[-1]}")
