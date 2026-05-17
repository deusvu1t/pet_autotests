# Шпаргалка — урок 2

## Приоритет локаторов (запомнить наизусть)

```
get_by_role  →  get_by_label  →  get_by_placeholder  →  get_by_text
              →  get_by_alt_text  →  get_by_title  →  get_by_test_id
              →  page.locator("css")  →  XPath
```

Чем выше — тем стабильнее и user-centric.

---

## Семь встроенных локаторов

| Метод                       | Когда                                | DOM-пример                                            |
|-----------------------------|--------------------------------------|-------------------------------------------------------|
| `get_by_role(role, name=)`  | Кликабельное / интерактивное         | `<button>Save</button>` → `("button", name="Save")`   |
| `get_by_label(text)`        | Поле формы со связанным `<label>`    | `<label>Email <input/></label>`                        |
| `get_by_placeholder(text)`  | Инпут без label                      | `<input placeholder="Search">`                         |
| `get_by_text(text)`         | Некликабельный элемент с текстом     | `<p>Welcome, John</p>`                                 |
| `get_by_alt_text(text)`     | Картинка                              | `<img alt="Logo">`                                     |
| `get_by_title(text)`        | Элемент с tooltip                    | `<span title="Help">?</span>`                          |
| `get_by_test_id(value)`     | Когда ничего выше не подходит        | `<div data-test="product-card">`                       |

---

## Параметры `get_by_role`

```python
page.get_by_role("heading", name="About", level=2)        # h2 only
page.get_by_role("button", name="Submit", exact=True)     # точное имя
page.get_by_role("button", name=re.compile("Add"))        # регулярка
page.get_by_role("checkbox", checked=True)
page.get_by_role("button", disabled=True)
page.get_by_role("button", expanded=False)
```

---

## ARIA-роли — самые ходовые

| HTML                           | role         |
|--------------------------------|--------------|
| `<button>`                     | `button`     |
| `<a href="...">`               | `link`       |
| `<input type="text">`          | `textbox`    |
| `<input type="email">`         | `textbox`    |
| `<input type="password">`      | `textbox`    |
| `<input type="checkbox">`      | `checkbox`   |
| `<input type="radio">`         | `radio`      |
| `<select>`                     | `combobox`   |
| `<option>`                     | `option`     |
| `<h1>` ... `<h6>`              | `heading`    |
| `<img alt="...">`              | `img`        |
| `<table>`                      | `table`      |
| `<tr>`                         | `row`        |
| `<th>`, `<td>`                 | `cell`       |
| `<nav>`                        | `navigation` |
| `<dialog>`                     | `dialog`     |
| `<form>`                       | `form`       |
| `<ul>`, `<ol>`                 | `list`       |
| `<li>`                         | `listitem`   |

---

## Цепочки

```python
# Scoping — поиск ВНУТРИ
form = page.get_by_role("form", name="Sign up")
form.get_by_role("button", name="Submit").click()

# Filter по тексту
card = page.locator(".product").filter(has_text="Hammer")

# Filter по дочернему элементу
card_with_btn = page.locator(".product").filter(
    has=page.get_by_role("button", name="Add")
)

# Обратные фильтры
in_stock = page.locator(".row").filter(has_not_text="Out of stock")
no_btn = page.locator(".product").filter(
    has_not=page.get_by_role("button", name="Add")
)

# Один из множества
items = page.locator(".item")
items.first              # первый
items.last               # последний
items.nth(2)             # третий (с 0)
items.count()            # сколько (синхронно — для ассертов используй expect)

# Логика
btn_a.and_(btn_b)        # И
status_loading.or_(status_done)   # ИЛИ
```

---

## Антипаттерны → как делать правильно

| ❌ Антипаттерн                          | ✅ Замена                                       |
|----------------------------------------|------------------------------------------------|
| `time.sleep(3)`                         | Ничего — Playwright сам ждёт                    |
| `page.wait_for_timeout(3000)`           | То же — убрать                                  |
| `time.sleep(2); expect(loc).visible()`  | Просто `expect(loc).to_be_visible()`            |
| `page.query_selector(...)`              | `page.locator(...)`                             |
| `page.locator("css").first.click()` без причины | Сузить scope: `parent.get_by_role(...)`         |
| `get_by_text("Save")` для кнопки        | `get_by_role("button", name="Save")`            |
| Куча XPath                              | `get_by_role` + `.filter()` решает 90%          |

---

## Если правда нужно подождать

```python
page.wait_for_url("**/dashboard")                # переход
page.wait_for_load_state("networkidle")          # сеть тиха ≥ 500мс
page.wait_for_load_state("domcontentloaded")     # DOM построен
locator.wait_for(state="visible")                # элемент стал виден
locator.wait_for(state="hidden")                 # пропал
locator.wait_for(state="attached")               # появился в DOM
locator.wait_for(state="detached")               # исчез из DOM
page.wait_for_response("**/api/products")        # пришёл ответ
page.wait_for_request("**/api/login")            # ушёл запрос
```

---

## Codegen и дебаг

```bash
playwright codegen https://practicesoftwaretesting.com/   # рекордер
playwright open https://practicesoftwaretesting.com/      # без записи

PWDEBUG=1 pytest tests/ui/                                # пошаговый дебаг
pytest --headed --slowmo 500                              # медленнее, видно
playwright show-trace test-results/.../trace.zip          # трейс упавшего
```

---

## Локаторы на нашем сайте (practicesoftwaretesting.com)

Сайт использует `data-test` (не `data-testid`!) — в `conftest.py` стоит:
```python
playwright.selectors.set_test_id_attribute("data-test")
```

Где использовать что:

| Элемент                   | Лучший локатор                                          |
|---------------------------|---------------------------------------------------------|
| Поле поиска               | `get_by_placeholder("Search")` или `get_by_test_id("search-query")` |
| Кнопка поиска             | `get_by_test_id("search-submit")`                       |
| Email/Password при логине | `get_by_label("Email address")`, `get_by_label("Password")` |
| Кнопка Login/Register     | `get_by_role("button", name="Login")`                   |
| Карточка товара           | `page.locator("[data-test^='product-']")`               |
| Цена в карточке           | `get_by_test_id("product-price")`                       |
| Корзина (иконка)          | `get_by_test_id("nav-cart")`                            |
| Sign in / Register в шапке| `get_by_role("link", name="Sign in")`                   |
