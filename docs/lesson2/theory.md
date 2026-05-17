# Урок 2 — Локаторы Playwright

## Что такое локатор

**Локатор** в Playwright — это **рецепт поиска элемента**, а не сам элемент.
Когда ты пишешь:

```python
button = page.get_by_role("button", name="Sign in")
```

— ты НЕ нашёл кнопку. Ты **описал, как её найти**. Реальный поиск произойдёт
в момент действия (`.click()`, `.fill()`, `.is_visible()`) или ассерта (`expect(...)`).

Это и называется **lazy** (ленивым) поиском.

### Зачем это знать

1. Локатор можно создать **до** того, как элемент появится на странице — и он
   "выстрелит" сам, когда нужно.
2. Локатор **переиспользуется** — один и тот же объект можно вызывать сколько угодно раз.
3. Локатор **самообновляется** — если страница перерисовалась, при следующем
   вызове он найдёт уже новый DOM-узел. Не будет stale-element error как в Selenium.

### Locator vs ElementHandle

В старом Playwright API был `ElementHandle` (`page.query_selector(...)`) — это
"ссылка на конкретный узел DOM". Если узел пересоздался — ссылка протухала.

**Никогда не используй `query_selector` и `ElementHandle`.** Это устаревший API.
Только `Locator` (методы `page.locator(...)`, `page.get_by_*(...)`).

---

## Auto-wait — почему `time.sleep` это зло

Каждое действие на локаторе (`.click()`, `.fill()`, `.check()`) и каждый
`expect(locator)` **сами ждут**, пока:

1. Элемент появится в DOM
2. Станет видимым (`visible: true`, не `display: none`)
3. Станет стабильным (не двигается)
4. Станет интерактивным (`enabled`, не закрыт оверлеем)
5. Получит фокус (для ввода)

Дефолтный таймаут — **30 секунд** на действие, **5 секунд** на `expect`. Настраивается.

### Антипаттерны, которые часто встречаются у новичков

```python
# ❌ Никогда так не делай
import time
time.sleep(5)
page.click("button")

# ❌ И так тоже нет
page.wait_for_timeout(5000)   # это просто sleep, обёрнутый в Playwright
page.click("button")

# ❌ И так
page.click("button")
time.sleep(2)
expect(page.get_by_text("Success")).to_be_visible()
```

Почему плохо:
- На быстрой машине ждёт лишнее → тесты медленнее в разы.
- На медленной всё равно может не успеть → тесты flaky.
- Это явный признак "автоматизатора-новичка" на собесе.

```python
# ✅ Правильно — Playwright сам всё ждёт
page.get_by_role("button", name="Submit").click()
expect(page.get_by_text("Success")).to_be_visible()
```

Если **реально** надо подождать конкретное условие — есть точечные ожидания:

```python
page.wait_for_url("**/dashboard")
page.wait_for_load_state("networkidle")
locator.wait_for(state="visible")
page.wait_for_response(lambda r: "/api/products" in r.url)
```

---

## Приоритет локаторов

Это **главное** в этой теме. На собесе спросят гарантированно.

Официальная рекомендация Playwright (от лучшего к худшему):

| Приоритет | Локатор                  | Зачем                                              |
|-----------|--------------------------|----------------------------------------------------|
| 1         | `get_by_role()`          | Стабилен, отражает то, что видит пользователь      |
| 2         | `get_by_label()`         | Для форм — естественный пользовательский подход    |
| 3         | `get_by_placeholder()`   | Для инпутов без label                              |
| 4         | `get_by_text()`          | Для нескликабельных элементов с текстом            |
| 5         | `get_by_alt_text()`      | Для картинок                                        |
| 6         | `get_by_title()`         | Для элементов с tooltip                            |
| 7         | `get_by_test_id()`       | Когда ничего из выше — не подходит/не стабильно    |
| 8         | `page.locator("css")`    | Когда даже `data-test` нет (старый легаси)          |
| 9         | XPath                    | Только когда CSS не справляется (редко)            |

**Идея:** локаторы первых уровней — это то, как пользователь видит сайт.
Они не сломаются, если разработчик переименует CSS-класс или поменяет структуру div'ов.
А `data-test` атрибут разработчик добавляет специально для тестов — он обычно
не "случайно меняется", но требует поддержки со стороны фронта.

> На `practicesoftwaretesting.com` много `data-test` атрибутов, поэтому в нашем
> проекте `get_by_test_id` будет частым гостем — но **не единственным**. Где
> уместно — используй `get_by_role` и `get_by_label`.

---

## Семь встроенных локаторов

### 1. `get_by_role(role, name=...)` — главный

Находит по **ARIA-роли** + опционально по **accessible name**.

```python
page.get_by_role("button", name="Sign in").click()
page.get_by_role("heading", name="Dashboard")
page.get_by_role("link", name="Products")
page.get_by_role("checkbox", name="I agree").check()
page.get_by_role("textbox", name="Email")
```

Параметры, которые часто пригодятся:
- `name=` — accessible name (текст внутри / aria-label / связанный label)
- `name=re.compile(...)` — регуляркой
- `exact=True` — точное совпадение (а не подстрокой)
- `checked=True/False` — для чекбоксов и радио
- `disabled=True/False`
- `expanded=True/False` — для аккордеонов и dropdown
- `level=N` — для headings (h1=1, h2=2, ...)

```python
page.get_by_role("heading", name="About us", level=2)
page.get_by_role("checkbox", checked=True)
```

#### Что такое ARIA-роль

ARIA — это спецификация доступности. У каждого HTML-элемента есть
**неявная роль** (implicit role):

| HTML                 | ARIA role     |
|----------------------|---------------|
| `<button>`           | `button`      |
| `<a href="...">`     | `link`        |
| `<input type="text">`| `textbox`     |
| `<input type="checkbox">` | `checkbox` |
| `<h1>...<h6>`        | `heading`     |
| `<select>`           | `combobox`    |
| `<table>`            | `table`       |
| `<img alt="...">`    | `img`         |
| `<nav>`              | `navigation`  |

Можно явно задать через `role="..."` — этим часто грешат фронтенд-фреймворки
(div с `role="button"`).

**Accessible name** — это что прочитает скринридер:
- Текст внутри (`<button>Save</button>` → name="Save")
- `aria-label="..."` 
- `<label for="email">Email</label>` — для связанного инпута

Чтобы посмотреть роли и имена — открой DevTools → вкладка **Accessibility**.

### 2. `get_by_label(text)` — для полей форм

Находит инпут по тексту его `<label>`. Это естественный путь:
"найди мне поле Email и введи туда значение".

```python
page.get_by_label("Email").fill("test@example.com")
page.get_by_label("I accept the terms").check()
```

Работает с тремя способами связи label с инпутом:

```html
<!-- 1) for/id -->
<label for="email">Email</label>
<input id="email" type="email" />

<!-- 2) обёртка -->
<label>Email <input type="email" /></label>

<!-- 3) aria-labelledby -->
<span id="lbl">Email</span>
<input aria-labelledby="lbl" type="email" />
```

### 3. `get_by_placeholder(text)`

Когда у инпута есть placeholder, но нет label — этим грешит много сайтов.

```python
page.get_by_placeholder("Search products...").fill("hammer")
```

Параметры: `exact=True`, можно регулярку.

### 4. `get_by_text(text)`

Для **некликабельных** элементов: текст параграфа, заголовок без `<h*>`,
сообщение об ошибке.

```python
expect(page.get_by_text("Welcome")).to_be_visible()       # частичное совпадение
expect(page.get_by_text("Welcome", exact=True)).to_be_visible()
expect(page.get_by_text(re.compile(r"\d+ items"))).to_be_visible()
```

⚠ Для кнопок и ссылок **не используй** `get_by_text` — есть `get_by_role`,
он точнее (`<button>Save</button>` и `<div>Save</div>` оба содержат текст
"Save", но `get_by_role("button", name="Save")` найдёт только кнопку).

### 5. `get_by_alt_text(text)`

Для картинок с `alt`:

```python
page.get_by_alt_text("Company logo").click()
```

### 6. `get_by_title(text)`

Для элементов с `title` (это tooltip при наведении):

```python
expect(page.get_by_title("Issues count")).to_have_text("25")
```

### 7. `get_by_test_id(value)`

По умолчанию ищет атрибут `data-testid`. На нашем сайте используется `data-test`,
поэтому в `conftest.py` мы переопределили:

```python
playwright.selectors.set_test_id_attribute("data-test")
```

```python
page.get_by_test_id("search-query").fill("hammer")
page.get_by_test_id("checkout-button").click()
```

---

## Цепочки и фильтры — то, что отделяет джуна от мидла

### Локаторы можно цеплять (`scoping`)

```python
# Найти кнопку Submit ВНУТРИ конкретной формы
form = page.get_by_role("form", name="Sign up")
form.get_by_role("button", name="Submit").click()

# То же через .locator()
page.locator(".sidebar").get_by_role("link", name="Logout").click()
```

Это решает 80% проблем с дубликатами на странице.

### `.filter()` — отбор по содержимому или дочерним элементам

```python
# Карточка товара, где есть текст "Hammer"
card = page.get_by_test_id("product").filter(has_text="Hammer")
card.get_by_role("button", name="Add to cart").click()

# Строки таблицы, где НЕТ текста "Out of stock"
in_stock_rows = page.get_by_role("row").filter(has_not_text="Out of stock")

# Карточка, внутри которой есть кнопка Add
card_with_add = page.get_by_test_id("product").filter(
    has=page.get_by_role("button", name="Add to cart")
)

# И обратное — карточка БЕЗ кнопки Add
card_without_add = page.get_by_test_id("product").filter(
    has_not=page.get_by_role("button", name="Add to cart")
)
```

### Доступ к одному из множества: `.first`, `.last`, `.nth(i)`

```python
products = page.get_by_test_id("product")
products.first.click()
products.last.click()
products.nth(2).click()   # третий по счёту (нумерация с 0)

# Сколько найдено
expect(products).to_have_count(9)
```

### `.and_()` и `.or_()`

```python
# Кнопка, которая И отключена, И с текстом "Submit"
btn = page.get_by_role("button", name="Submit").and_(
    page.get_by_role("button", disabled=True)
)

# Любая из двух надписей: "Loading..." или "Done"
status = page.get_by_text("Loading...").or_(page.get_by_text("Done"))
expect(status).to_be_visible()
```

`.or_()` особенно полезен, когда нужно дождаться **одного из** состояний.

---

## Strict mode — типичный баг

В Playwright **по умолчанию strict mode**: если локатор находит больше одного
элемента, действие на нём упадёт с ошибкой:

```
Locator.click: Error: strict mode violation: locator(...)
resolved to 3 elements
```

Это спасает от случайных кликов "не туда". Чинится тремя способами:

```python
# 1) Уточнить локатор (лучший вариант)
page.get_by_role("button", name="Add to cart").nth(0).click()  # явно первый

# 2) Использовать .first / .last
page.get_by_role("button", name="Add to cart").first.click()

# 3) Сузить scope
page.get_by_test_id("featured-products") \
    .get_by_role("button", name="Add to cart").click()
```

Третий вариант предпочтительнее — он отражает намерение
("добавь товар из featured-секции"), а не "добавь первый попавшийся".

> `expect(locator).to_have_count(N)` НЕ проверяет strict mode — он работает
> с массивом найденных элементов.

---

## CSS и XPath — когда без них

Если ничего из встроенных локаторов не подходит:

```python
# CSS
page.locator("div.product-card[data-id='42']")
page.locator("ul > li.active")

# XPath (начинается с // или /)
page.locator("//div[contains(@class, 'card')]//button")
page.locator("xpath=//button[text()='Save']")
```

Когда оправданы:
- Сложная иерархическая выборка (например, "элемент рядом с другим")
- Псевдоклассы CSS, которых нет в Playwright (`:nth-child`, `:has`)

XPath — последний вариант. Он:
- Хрупкий (зависит от структуры DOM)
- Сложно читается
- Медленнее CSS
- Каждое изменение вёрстки → переписывать

Если видишь в проекте много XPath — это красный флаг.

---

## `playwright codegen` — генератор локаторов

Запусти из терминала:

```bash
playwright codegen https://practicesoftwaretesting.com/
```

Откроется браузер + окно с кодом. Кликаешь по элементам — Playwright
показывает, какой локатор он бы предложил. Используй для:

- Быстрого старта в незнакомом UI
- Подбора правильного `get_by_role(...)` (а не угадывания ARIA)
- Дебага: "почему мой локатор не находит элемент?" — наведи мышью в codegen,
  посмотри, что предлагает Playwright

Для дебага уже написанных тестов:

```bash
PWDEBUG=1 pytest tests/ui/test_home.py -k test_search
```

или через флаг:

```bash
pytest tests/ui/test_home.py --headed --slowmo 500
```

---

## Главные тейкауэи

1. **Локатор — рецепт, не элемент.** Lazy, переиспользуемый, не stale.
2. **Никаких `time.sleep`.** Auto-wait встроен в каждое действие.
3. **Приоритет: role → label → placeholder → text → testid.**
4. **Strict mode** ловит дубли — не глуши его через `.first` бездумно,
   сначала попробуй сузить scope через цепочку.
5. **`.filter()`** — про "карточка, в которой...". Это очень мощный инструмент.
6. **Codegen** — твой друг, особенно в начале.
